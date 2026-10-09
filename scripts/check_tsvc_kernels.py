#!/usr/bin/env python3
"""Compile parameterized TSVC kernels and compare full state to source references.

This is an extraction/differential test, not a proof. Candidate C is executable
code: run untrusted candidates only in an appropriately isolated environment.
"""

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIZES = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 15, 16, 17, 31, 32, 33,
                 40, 63, 64, 65, 66, 67, 127, 128, 129, 257]
DEFAULT_MATRIX_SIZES = [0, 1, 2, 3, 4, 5, 7, 8, 9, 15, 16, 17, 31, 32, 33]
DEFAULT_STRIDE_PADDINGS = [0, 1, 5]
INDEX_PATTERNS = ["identity", "reverse", "all_zero", "all_last", "permutation", "random_with_replacement"]
SELECTOR_PATTERNS = ["case_1", "case_2", "case_3", "case_4", "default_zero", "default_negative",
                     "default_large", "cyclic_with_int_limits", "random_with_int_limits"]
STOP_PATTERNS = ["none", "first", "middle", "last"]

DRIVER_SUPPORT = r'''
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <limits.h>

typedef struct { int *base; int *data; int total; int guard; int count; } Buffer;
static uint32_t rng_state;

static uint32_t next_random(void) {
    rng_state = rng_state * UINT32_C(1664525) + UINT32_C(1013904223);
    return rng_state;
}

static int sample(int trial, int i) {
    if (trial == 0) return 0;
    if (trial == 1) return 1;
    if (trial == 2) return -1;
    if (trial == 3) return i % 2 ? -1 : 1;
    return (int)(next_random() % 7) - 3;
}

static int sentinel(int i) { return 123456789 + i; }

static Buffer allocate_buffer(int n, int guard) {
    int count = n ? n : 1;
    int total = count + 2 * guard;
    int *base = malloc((size_t)total * sizeof(*base));
    if (!base) { fprintf(stderr, "allocation failed\n"); exit(2); }
    Buffer result = {base, base + guard, total, guard, count};
    return result;
}

static Buffer make_input(int n, int trial, int guard) {
    Buffer result = allocate_buffer(n, guard);
    for (int i = 0; i < result.total; ++i) result.base[i] = sentinel(i);
    for (int i = 0; i < result.count; ++i) result.data[i] = sample(trial, i);
    return result;
}

static Buffer copy_input(Buffer source, int n, int guard) {
    Buffer result = allocate_buffer(n, guard);
    memcpy(result.base, source.base, (size_t)result.total * sizeof(int));
    return result;
}

static void fill_indices(Buffer buffer, int n, int pattern) {
    int bound = n ? n : 1;
    for (int i = 0; i < buffer.count; ++i) {
        switch (pattern) {
            case 0: case 4: buffer.data[i] = i % bound; break;
            case 1: buffer.data[i] = bound - 1 - i % bound; break;
            case 2: buffer.data[i] = 0; break;
            case 3: buffer.data[i] = bound - 1; break;
            case 5: buffer.data[i] = (int)(next_random() % (uint32_t)bound); break;
            default: fprintf(stderr, "unknown index pattern\n"); exit(2);
        }
    }
    if (pattern == 4)
        for (int i = n - 1; i > 0; --i) {
            int j = (int)(next_random() % (uint32_t)(i + 1));
            int tmp = buffer.data[i];
            buffer.data[i] = buffer.data[j];
            buffer.data[j] = tmp;
        }
}

static void fill_selectors(Buffer buffer, int pattern) {
    static const int choices[] = {1,2,3,4,0,-1,5,INT_MIN,INT_MAX};
    for (int i = 0; i < buffer.count; ++i) {
        int choice = pattern < 7 ? pattern : pattern == 7 ? i % 9 : (int)(next_random() % 9);
        buffer.data[i] = choices[choice];
    }
}

static void prepare_squares(Buffer e, int n) {
    if (n > 5) e.data[0] = (e.data[0] > 0) - (e.data[0] < 0);
}

static void prepare_product(Buffer a, int n, int trial) {
    for (int i = 0; i < a.count; ++i) {
        if (trial == 0) a.data[i] = 0;
        else if (trial == 1) a.data[i] = 1;
        else if (trial == 2) a.data[i] = -1;
        else if (trial == 3) a.data[i] = i % 2 ? -1 : 1;
        else if (trial == 4 || trial == 5) a.data[i] = i < 18 ? 3 : 1;
        else if (trial == 6) a.data[i] = i < 18 ? (i % 2 ? -2 : 3) : (i % 2 ? -1 : 1);
        else {
            int magnitude = i < 18 ? 2 + (int)((next_random() >> 16) % 2) : 1;
            a.data[i] = next_random() & UINT32_C(0x10000) ? -magnitude : magnitude;
        }
    }
    if (trial == 4 && n) a.data[n / 2] = 0;
}

static void prepare_recurrence(Buffer b, Buffer *c, int n, int trial) {
    /* Small n can safely exercise both full-range coefficients. For larger
       n at most one unit-magnitude predecessor contributes to each result. */
    if (n <= 8) return;
    for (int i = 0; i < n; ++i) {
        b.data[i] = (b.data[i] > 0) - (b.data[i] < 0);
        if (c) {
            c->data[i] = (c->data[i] > 0) - (c->data[i] < 0);
            int choice = trial == 1 ? 1 : trial == 2 ? 2 : trial < 4 ? i % 2 + 1
                         : (int)(next_random() % 3);
            if (choice != 1) b.data[i] = 0;
            if (choice != 2) c->data[i] = 0;
        }
    }
}

static void prepare_triangular(Buffer coefficients, int n, int ld, int trial) {
    if (n <= 8) return;
    for (int i = 1; i < n; ++i) {
        int j = trial % 4 == 0 ? 0 : trial % 4 == 1 ? i-1 : trial % 4 == 2 ? i/2
                : (int)(next_random() % (uint32_t)i);
        int value = coefficients.data[j*ld+i];
        value = (value > 0) - (value < 0);
        for (int k = 0; k < i; ++k) coefficients.data[k*ld+i] = k == j ? value : 0;
    }
}

static void prepare_triangular_squares(Buffer aa, Buffer bb, int n, int ld) {
    if (n <= 5) return;
    for (int j = 1; j < n; ++j) {
        int previous = aa.data[j*ld];
        for (int i = 1; i <= j; ++i) {
            int target = -bb.data[j*ld+i];
            bb.data[j*ld+i] = target - previous*previous;
            previous = target;
        }
    }
}

static void prepare_wavefront(Buffer aa, int n, int ld, int trial) {
    if (n <= 8) return;
    int u = sample(trial, 0), v = sample(trial, 1);
    int wave[6] = {u, v, v-u, -u, -v, u-v};
    /* f(k-1)+f(k+1)=f(k); F(row,col)=f(col-row). Only boundaries
       are prepared. Original interior values remain independent inputs. */
    for (int i = 0; i < n; ++i) {
        aa.data[i] = wave[i%6];
        aa.data[i*ld] = wave[(6-i%6)%6];
    }
}

static void prepare_vbor_input(Buffer input, int n, int trial) {
    for (int i = 0; i < n; ++i) {
        int value = input.data[i];
        input.data[i] = trial == 4 ? 2 : trial == 5 ? -2 : value < -2 ? -2 : value > 2 ? 2 : value;
    }
}

static void prepare_trig(Buffer b, Buffer c, int n, int trial) {
    if (trial < 4) return;
    static const int values[] = {0,1,-1,2,-2,3,-3,INT_MIN,INT_MAX,1000,-1000};
    for (int i = 0; i < n; ++i) {
        b.data[i] = values[(i+trial)%11];
        c.data[i] = values[(3*i+2*trial)%11];
    }
}

static void prepare_termination(Buffer d, int n, int pattern) {
    int stop = pattern == 0 ? n : pattern == 1 ? 0 : pattern == 2 ? n/2 : n-1;
    for (int i = 0; i < stop; ++i) if (d.data[i] < 0) d.data[i] = -d.data[i];
    if (n && stop < n) d.data[stop] = -1;
}

static void fill_row_padding(Buffer buffer, int n, int ld) {
    for (int col = n; col < ld; ++col) buffer.data[col] = sentinel(col);
}

static void check_row_padding(const char *name, const char *array, int n, int ld,
                              Buffer actual, Buffer expected) {
    for (int col = n; col < ld; ++col)
        if (actual.data[col] != sentinel(col) || expected.data[col] != sentinel(col)) {
            fprintf(stderr, "%s: %s single-row padding [0][%d] modified\n", name, array, col);
            exit(1);
        }
}

static void fill_padding(Buffer buffer, int n, int ld) {
    for (int row = 0; row < n; ++row)
        for (int col = n; col < ld; ++col) {
            int index = row * ld + col;
            buffer.data[index] = sentinel(index);
        }
}

static void check_padding(const char *name, const char *array, int n, int ld,
                          Buffer actual, Buffer expected) {
    for (int row = 0; row < n; ++row)
        for (int col = n; col < ld; ++col) {
            int index = row * ld + col;
            if (actual.data[index] != sentinel(index) || expected.data[index] != sentinel(index)) {
                fprintf(stderr, "%s: %s row padding [%d][%d] modified (n=%d ld=%d)\n",
                        name, array, row, col, n, ld);
                exit(1);
            }
        }
}

static void compare(const char *name, const char *array, int n, int ld, int trial,
                    int index_pattern, Buffer actual, Buffer expected) {
    for (int i = 0; i < actual.total; ++i) {
        int is_guard = i < actual.guard || i >= actual.guard + actual.count;
        if (actual.base[i] != expected.base[i] ||
            (is_guard && (actual.base[i] != sentinel(i) || expected.base[i] != sentinel(i)))) {
            fprintf(stderr, "%s: %s[%d] n=%d ld=%d trial=%d pattern=%d guard=%d: got %d, expected %d%s\n",
                    name, array, i - actual.guard, n, ld, trial, index_pattern, actual.guard,
                    actual.base[i], expected.base[i], is_guard ? " (guard write)" : "");
            exit(1);
        }
    }
    free(actual.base);
    free(expected.base);
}
'''


def is_matrix(case: dict) -> bool:
    return bool(case["contract"].get("row_stride"))


def is_indexed(case: dict) -> bool:
    return any(array.get("index_domain") for array in case["contract"]["arrays"])


def has_selectors(case: dict) -> bool:
    return any(array.get("selector_domain") for array in case["contract"]["arrays"])


def pattern_count(case: dict) -> int:
    stop = bool(case["contract"].get("termination"))
    if sum((is_indexed(case), has_selectors(case), stop)) > 1:
        raise ValueError("combined index/selector/termination patterns need a separate review")
    return (len(INDEX_PATTERNS) if is_indexed(case) else len(SELECTOR_PATTERNS) if has_selectors(case)
            else len(STOP_PATTERNS) if stop else 1)


def eligible_sizes(case: dict, sizes: list[int], matrix_sizes: list[int]) -> list[int]:
    bounds = case["contract"]["size"]
    if bounds["multiple_of"] < 1:
        raise ValueError("invalid size divisibility contract")
    requested = matrix_sizes if is_matrix(case) else sizes
    return [n for n in requested if bounds["minimum"] <= n <= bounds["maximum"]
            and n % bounds["multiple_of"] == 0 and n not in bounds.get("excluded", [])]


def execution_count(cases: list[dict], sizes: list[int], trials: int,
                    matrix_sizes: list[int], stride_paddings: list[int]) -> int:
    return sum(len(eligible_sizes(case, sizes, matrix_sizes)) * trials * 2
               * (len(stride_paddings) if is_matrix(case) else 1)
               * pattern_count(case) for case in cases)


def scalar_test_value(scalar: dict, ordinal: int = 0) -> str:
    domain = scalar.get("domain", {}).get("id", "int")
    # Do not give every unrestricted scalar the same value: that would hide
    # substituting s1 for s2 in cases such as s242. Preserve single-scalar trials.
    values = {
        "int": "(trial % 7) - 3" if ordinal == 0 else f"((trial + {3 * ordinal}) % 7) - 3",
        "start_1based": "trial % 4 == 0 ? 1 : trial % 4 == 1 ? n+1 : trial % 4 == 2 ? (n ? n : 1) : n/2+1",
        "matrix_row_1based": "trial % 3 == 0 ? 1 : trial % 3 == 1 ? (n ? n : 1) : n/2+1",
        "nonnegative_offset": "trial % 4 == 0 ? 0 : trial % 4 == 1 ? 1 : trial % 4 == 2 ? n+3 : n/2",
        # A three-trial period exercises all 4x3 start/step combinations over
        # the default 12 trials, rather than correlating every step=2 with an empty loop.
        "positive_step": "trial % 3 == 0 ? 1 : trial % 3 == 1 ? 2 : n+3",
        "signed_offset": "trial % 4 == 0 ? -2 : trial % 4 == 1 ? 0 : trial % 4 == 2 ? 1 : n+3",
        "nonnegative_stride": "trial % 4 == 0 ? 0 : trial % 4 == 1 ? 1 : trial % 4 == 2 ? 2 : 5",
        "half_length": "trial % 3 == 0 ? 0 : trial % 3 == 1 ? n/2 : n/4",
    }
    if domain not in values:
        raise ValueError(f"unreviewed scalar test domain: {domain}")
    return values[domain]


def driver(cases: list[dict], sizes: list[int], trials: int, seed: int, *,
           matrix_sizes: list[int] | None = None, stride_paddings: list[int] | None = None) -> str:
    matrix_sizes = DEFAULT_MATRIX_SIZES if matrix_sizes is None else matrix_sizes
    stride_paddings = DEFAULT_STRIDE_PADDINGS if stride_paddings is None else stride_paddings
    sections = [DRIVER_SUPPORT]
    for case in cases:
        name = case["name"]
        descriptors = {entry["name"]: entry for entry in case["contract"]["arrays"]}
        for output in case["contract"].get("scalar_outputs", []):
            if output["parameter"] in descriptors or output["minimum_elements"] != 1:
                raise ValueError("invalid scalar output descriptor")
            descriptors[output["parameter"]] = {**output, "layout": "scalar"}
        arrays = {name: entry.get("layout", "vector") for name, entry in descriptors.items()}
        scalars = [entry["name"] for entry in case["contract"]["scalar_inputs"]]
        matrix = is_matrix(case)
        sig = case["signature"]
        sections += [sig + ";", sig.replace(f" {name}(", f" reference_{name}(") + ";"]
        ld_param = ", int ld" if matrix else ""
        body = [f"static void test_{name}(int n, int trial, int guard{ld_param}) {{"]
        patterns = pattern_count(case)
        pattern = "index_pattern" if patterns > 1 else "-1"
        if patterns > 1:
            body.append(f"    for (int index_pattern = 0; index_pattern < {patterns}; ++index_pattern) {{")
        for ordinal, scalar in enumerate(case["contract"]["scalar_inputs"]):
            body.append(f"    int scalar_{scalar['name']} = {scalar_test_value(scalar, ordinal)};")
        extents = {}
        for array, layout in arrays.items():
            if not matrix and layout in ("row_major_matrix", "flat_square"):
                raise ValueError("matrix/flat-square storage requires a row-stride contract")
            if layout == "offset_vector":
                offset = descriptors[array]["offset_parameter"]
                if offset not in scalars:
                    raise ValueError("offset-vector parameter missing from scalar inputs")
                offset_value = f"scalar_{offset}"
                if descriptors[array].get("clamp_negative_offset"):
                    offset_value = f"({offset_value} > 0 ? {offset_value} : 0)"
                extent = f"n + {offset_value}"
            elif layout == "extended_vector":
                extra = descriptors[array]["extra_elements"]
                if not isinstance(extra, int) or not 1 <= extra <= 64:
                    raise ValueError("unreviewed extended-vector test allocation")
                extent = f"n + {extra}"
            elif layout == "strided_vector":
                stride = descriptors[array]["stride_parameter"]
                if stride not in scalars:
                    raise ValueError("stride parameter missing from scalar inputs")
                extent = f"n * scalar_{stride}"
            else:
                extent = {"vector": "n", "row_major_matrix": "n * ld", "flat_square": "n * n", "scalar": "1"}[layout]
                if layout == "row_major_matrix" and "logical_rows" in descriptors[array]:
                    if descriptors[array]["logical_rows"] != 1 or descriptors[array].get("logical_columns") != "n":
                        raise ValueError("unreviewed matrix shape")
                    extent = "ld"
            extents[array] = extent
            body.append(f"    Buffer got_{array} = make_input({extent}, trial, guard);")
            if layout == "row_major_matrix":
                fill = "fill_row_padding" if descriptors[array].get("logical_rows") == 1 else "fill_padding"
                body.append(f"    {fill}(got_{array}, n, ld);")
            if descriptors[array].get("index_domain"):
                domain = descriptors[array]["index_domain"]
                if (domain["minimum"] != 0 or domain["maximum_exclusive"] != "n"
                        or domain["positions"] != "0 <= i < n" or domain["duplicates_allowed"] is not True):
                    raise ValueError("unreviewed index test domain")
                body.append(f"    fill_indices(got_{array}, n, index_pattern);")
            if descriptors[array].get("selector_domain"):
                domain = descriptors[array]["selector_domain"]
                if (domain["cases"] != [1, 2, 3, 4] or domain["default"] != "fall through to case 1"
                        or domain["values"] != "any signed 32-bit int"):
                    raise ValueError("unreviewed selector domain")
                body.append(f"    fill_selectors(got_{array}, index_pattern);")
        profile = case.get("testing", {}).get("profile", "default")
        preparation = {
            "default": "",
            "bounded_product": "prepare_product(got_a, n, trial);",
            "first_order_recurrence": "prepare_recurrence(got_b, NULL, n, trial);",
            "second_order_recurrence": "prepare_recurrence(got_b, &got_c, n, trial);",
            "repeated_square": "prepare_squares(got_e, n);",
            "triangular_recurrence": f"prepare_triangular(got_{'aa' if 'aa' in arrays else 'bb'}, n, ld, trial);",
            "triangular_squares": "prepare_triangular_squares(got_aa, got_bb, n, ld);",
            "wavefront": "prepare_wavefront(got_aa, n, ld, trial);",
            "bounded_vbor": "\n    ".join(f"prepare_vbor_input(got_{key}, n, trial);" for key in ("a", "b", "c", "d", "e", "aa")),
            "integer_trig": "prepare_trig(got_b, got_c, n, trial);",
            "termination": "prepare_termination(got_d, n, index_pattern);",
        }
        if profile not in preparation:
            raise ValueError(f"unreviewed test-input profile: {profile}")
        if preparation[profile]:
            body.append("    " + preparation[profile])
        for array, extent in extents.items():
            body.append(f"    Buffer want_{array} = copy_input(got_{array}, {extent}, guard);")
        for prefix, function in (("want", f"reference_{name}"), ("got", name)):
            args = [f"{prefix}_{array}.data" for array in arrays]
            args += [f"scalar_{scalar}" for scalar in scalars] + ["n"] + (["ld"] if matrix else [])
            lhs = f"int {prefix}_result = " if case["contract"]["scalar_output"] else ""
            body.append(f"    {lhs}{function}({', '.join(args)});")
        if case["contract"]["scalar_output"]:
            body.append(f'''    if (got_result != want_result) {{
        fprintf(stderr, "{name}: scalar n=%d trial=%d pattern=%d: got %d, expected %d\\n",
                n, trial, {pattern}, got_result, want_result);
        exit(1);
    }}''')
        for array, layout in arrays.items():
            if layout == "row_major_matrix":
                check = "check_row_padding" if descriptors[array].get("logical_rows") == 1 else "check_padding"
                body.append(f'    {check}("{name}", "{array}", n, ld, got_{array}, want_{array});')
            body.append(f'    compare("{name}", "{array}", n, {"ld" if matrix else "0"}, trial, {pattern}, got_{array}, want_{array});')
        if patterns > 1:
            body.append("    }")
        body.append("}")
        sections.append("\n".join(body))
    groups = []
    for matrix, group_sizes in ((False, sizes), (True, matrix_sizes)):
        selected = [case for case in cases if is_matrix(case) == matrix]
        if not selected:
            continue
        invocations = []
        for case in selected:
            bounds = case["contract"]["size"]
            condition = f"sizes[i] >= {bounds['minimum']} && sizes[i] <= {bounds['maximum']} && sizes[i] % {bounds['multiple_of']} == 0"
            for excluded in bounds.get("excluded", []):
                if not isinstance(excluded, int) or excluded < 0:
                    raise ValueError("invalid excluded size")
                condition += f" && sizes[i] != {excluded}"
            invocations.append(f'                if ({condition}) test_{case["name"]}(sizes[i], trial, guard{", ld" if matrix else ""});')
        calls = "\n".join(invocations)
        padding_loop = ""
        if matrix:
            padding_loop = f'''for (size_t p = 0; p < sizeof(paddings)/sizeof(paddings[0]); ++p) {{
                int ld = (sizes[i] ? sizes[i] : 1) + paddings[p];'''
        groups.append(f'''    {{
        const int sizes[] = {{{', '.join(map(str, group_sizes))}}};
        for (size_t i = 0; i < sizeof(sizes) / sizeof(sizes[0]); ++i)
            for (int trial = 0; trial < {trials}; ++trial)
                for (int mode = 0; mode < 2; ++mode) {{
                    /* Exact buffers expose OOB reads to ASan; guarded buffers
                       independently detect writes beyond the allocation. */
                    int guard = mode == 0 ? 0 : 16;
                    {padding_loop}
{calls}
                    {"}" if matrix else ""}
                }}
    }}''')
    count = execution_count(cases, sizes, trials, matrix_sizes, stride_paddings)
    sections.append(f'''int main(void) {{
    const int paddings[] = {{{', '.join(map(str, stride_paddings))}}};
    rng_state = UINT32_C({seed});
{chr(10).join(groups)}
    puts("PASS: {len(cases)} kernels, {count} differential executions");
    return 0;
}}''')
    return "\n\n".join(sections) + "\n"


def run_checks(directory: Path, *, cc: str = "clang", names: list[str] | None = None,
               sizes: list[int] | None = None, trials: int = 12, seed: int = 1,
               sanitize: bool = False, candidate_dir: Path | None = None,
               matrix_sizes: list[int] | None = None, stride_paddings: list[int] | None = None) -> dict:
    sizes = DEFAULT_SIZES if sizes is None else sizes
    matrix_sizes = DEFAULT_MATRIX_SIZES if matrix_sizes is None else matrix_sizes
    stride_paddings = DEFAULT_STRIDE_PADDINGS if stride_paddings is None else stride_paddings
    # Data in [-3,3], plus the per-case product/recurrence preparation, is safe
    # at these sizes. Larger experiments need a reviewed input domain.
    if not sizes or any(n < 0 or n > 4096 for n in sizes):
        raise ValueError("test sizes must be in [0, 4096]")
    if not matrix_sizes or any(n < 0 or n > 128 for n in matrix_sizes):
        raise ValueError("matrix test sizes must be in [0, 128] for the reviewed input/resource domain")
    if not stride_paddings or any(p < 0 or p > 64 for p in stride_paddings):
        raise ValueError("stride paddings must be in [0, 64]")
    if trials < 1 or trials > 1000 or not 0 <= seed <= 0xFFFFFFFF:
        raise ValueError("trials must be in [1, 1000]; seed must be uint32")
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest["schema_version"] not in (1, 2, 3, 4, 5, 6):
        raise ValueError("unsupported manifest schema")
    available = {case["name"]: case for case in manifest["cases"] if case["status"] == "generated"}
    if names and (len(set(names)) != len(names) or set(names) - available.keys()):
        raise ValueError("--case must identify unique generated cases, not needs_review cases")
    cases = [available[name] for name in names] if names else list(available.values())
    if not cases:
        raise ValueError("no generated cases selected")
    if candidate_dir and not names:
        raise ValueError("use --case to select candidates explicitly")
    libraries = sorted({library for case in cases for library in
                        case["contract"].get("numeric_adaptation", {}).get("link_libraries", [])})
    if set(libraries) - {"m"}:
        raise ValueError("unreviewed link libraries")
    inputs, tested_sizes, excluded_sizes = [], {}, {}
    for case in cases:
        requested = matrix_sizes if is_matrix(case) else sizes
        valid = eligible_sizes(case, sizes, matrix_sizes)
        if not valid:
            raise ValueError(f"no requested sizes satisfy {case['name']} contract")
        tested_sizes[case["name"]] = valid
        excluded_sizes[case["name"]] = [n for n in requested if n not in valid]
        kernel = candidate_dir / f"{case['name']}.c" if candidate_dir else directory / case["kernel"]
        reference = directory / case["reference"]
        inputs.append((case["name"], kernel, reference))
    report = {
        "status": "failed",
        "kind": "differential_testing_not_formal_verification",
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "source_sha256": manifest["source_sha256"],
        "cases": [case["name"] for case in cases],
        "sizes": sizes, "matrix_sizes": matrix_sizes, "stride_paddings": stride_paddings,
        "trials": trials, "seed": seed, "sanitize": sanitize,
        "input_domain": "logical data in [-3,3] with per-case overflow-safe profiles; bounded indices, arbitrary-int selector patterns and domain-specific scalar inputs; matrix padding contains distinct canaries",
        "test_profiles": {case["name"]: case.get("testing", {"profile": "default"}) for case in cases},
        "scalar_output_cases": [case["name"] for case in cases if case["contract"].get("scalar_outputs")],
        "matrix_cases": [case["name"] for case in cases if is_matrix(case)],
        "indexed_cases": [case["name"] for case in cases if is_indexed(case)],
        "index_patterns": INDEX_PATTERNS,
        "selector_patterns": SELECTOR_PATTERNS,
        "selector_cases": [case["name"] for case in cases if has_selectors(case)],
        "pointer_view_cases": [case["name"] for case in cases if case["contract"].get("pointer_views")],
        "single_row_cases": [case["name"] for case in cases if any(a.get("logical_rows") == 1 for a in case["contract"]["arrays"])],
        "termination_cases": [case["name"] for case in cases if case["contract"].get("termination")],
        "stop_patterns": STOP_PATTERNS,
        "experiment_caveats": {case["name"]: case["experiment_caveats"] for case in cases if case.get("experiment_caveats")},
        "link_libraries": libraries,
        "tested_sizes": tested_sizes, "excluded_sizes": excluded_sizes,
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "candidate_directory": str(candidate_dir) if candidate_dir else None,
        "executions": execution_count(cases, sizes, trials, matrix_sizes, stride_paddings),
        "inputs": [{"case": name,
                    "kernel_sha256": hashlib.sha256(kernel.read_bytes()).hexdigest(),
                    "reference_sha256": hashlib.sha256(reference.read_bytes()).hexdigest()}
                   for name, kernel, reference in inputs],
        "commands": [],
    }
    compiler = shlex.split(cc)
    if not compiler:
        raise ValueError("empty compiler command")

    def execute(command: list[str], timeout: int = 120) -> str:
        report["commands"].append(command)
        env = dict(os.environ)
        if sanitize:
            # Make any sanitizer finding a failure even if the user's defaults
            # request recovery. Don't change compiler arithmetic semantics.
            env["ASAN_OPTIONS"] = "halt_on_error=1"
            env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env)
        if result.returncode:
            raise RuntimeError(f"command failed ({result.returncode}): {shlex.join(command)}\n"
                               + result.stdout + result.stderr)
        return result.stdout

    try:
        report["compiler"] = execute(compiler + ["--version"])
        with tempfile.TemporaryDirectory(prefix="tsvc-check-") as temp:
            build = Path(temp)
            cdriver = build / "driver.c"
            cdriver.write_text(driver(cases, sizes, trials, seed, matrix_sizes=matrix_sizes,
                                      stride_paddings=stride_paddings))
            report["driver_sha256"] = hashlib.sha256(cdriver.read_bytes()).hexdigest()
            interfaces = build / "interfaces.h"
            interfaces.write_text("\n".join(case["signature"] + ";" for case in cases) + "\n")
            flags = ["-std=c11", "-g"]
            if sanitize:
                flags += ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer"]
            objects = []
            for name, kernel, reference in inputs:
                for label, source, opt in (("kernel", kernel, "-O2"), ("ref", reference, "-O0")):
                    obj = build / f"{name}-{label}.o"
                    # Force the reviewed prototype into the kernel translation
                    # unit: a wrong candidate ABI must fail at compile time.
                    includes = ["-include", str(interfaces)] if label == "kernel" else []
                    execute(compiler + flags + includes + [opt, "-c", str(source), "-o", str(obj)])
                    objects.append(str(obj))
            binary = build / "check"
            execute(compiler + flags + ["-O2", str(cdriver), *objects, *(f"-l{lib}" for lib in libraries), "-o", str(binary)])
            report["stdout"] = execute([str(binary)], timeout=60)
            report["status"] = "passed_differential_tests"
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        report["error"] = str(error)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "generated/tsvc-kernels")
    parser.add_argument("--cc", default=os.environ.get("CC", "clang"))
    parser.add_argument("--case", dest="names", action="append")
    parser.add_argument("--sizes", nargs="+", type=int, default=DEFAULT_SIZES, help="1D test sizes")
    parser.add_argument("--matrix-sizes", nargs="+", type=int, default=DEFAULT_MATRIX_SIZES,
                        help="Logical square side lengths or single-row column counts (0..128)")
    parser.add_argument("--stride-paddings", nargs="+", type=int, default=DEFAULT_STRIDE_PADDINGS,
                        help="Matrix ld = max(1,n) + padding (each padding 0..64)")
    parser.add_argument("--trials", type=int, default=12)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--sanitize", action="store_true")
    parser.add_argument("--candidate-dir", type=Path)
    parser.add_argument("--report", type=Path, help="Save the reproducible validation report as JSON")
    args = parser.parse_args()
    try:
        report = run_checks(args.directory, cc=args.cc, names=args.names, sizes=args.sizes,
                            trials=args.trials, seed=args.seed, sanitize=args.sanitize,
                            candidate_dir=args.candidate_dir, matrix_sizes=args.matrix_sizes,
                            stride_paddings=args.stride_paddings)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + "\n")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"error: {error}\n")
    if report["status"] != "passed_differential_tests":
        parser.exit(1, report["error"] + "\n")
    print(report["stdout"], end="")
    for name, sizes in report["excluded_sizes"].items():
        if sizes:
            print(f"{name}: tested sizes {report['tested_sizes'][name]}; excluded by contract: {sizes}")
    if args.report:
        print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
