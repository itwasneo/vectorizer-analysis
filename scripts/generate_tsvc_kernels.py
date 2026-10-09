#!/usr/bin/env python3
"""Generate reviewed, parameterized integer kernels and a full 151-case inventory.

This extractor is intentionally specific to the reviewed TSVC source snapshot.
It is not a general-purpose C parser. Unreviewed cases are inventoried, not emitted.
"""

import argparse
import hashlib
import json
import re
import textwrap
from pathlib import Path

from extract_tsvc_int import DEFAULT_SOURCE, ROOT, closing_brace, functions
from tsvc_kernel_specs import (
    DEFERRED_REASONS, HELPERS, REVIEWED_SOURCE_SHA256, SCALAR_DOMAINS, SPECS, TEST_PROFILES, KernelSpec,
)

REPETITION = re.compile(
    r"for\s*\(int\s+nl\s*=\s*0;\s*nl\s*<\s*([^;]+);\s*nl\+\+\)\s*\{"
)
COMMENTS_OR_STRINGS = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/')
MAX_N = 2147483647 // 2
# Keeps n*n, packed-array induction variables, and their final increments in int.
MAX_MATRIX_N = 46340


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def without_comments(text: str) -> str:
    def replace(match: re.Match) -> str:
        value = match.group()
        if value.startswith(("//", "/*")):
            return re.sub(r"[^\n]", " ", value)
        return value
    return COMMENTS_OR_STRINGS.sub(replace, text)


def inventory(source: str) -> list[dict]:
    funcs = functions(source)
    main = without_comments(funcs["main"][2])
    category = None
    cases = []
    for line in main.splitlines():
        conditional = re.fullmatch(r"\s*#if TESTS & (\w+)\s*", line)
        if conditional:
            category = conditional[1]
        elif line.strip().startswith("#endif"):
            category = None
        else:
            call = re.fullmatch(r"\s*((?:s\d+|v[a-z]+))\(([^;]*)\);\s*", line)
            if not call:
                continue
            name = call[1]
            if category is None or name not in funcs:
                raise ValueError(f"unexpected call in main: {line}")
            start, end, body = funcs[name]
            cases.append({
                "name": name,
                "category": category,
                "original_call": line.strip(),
                "source_lines": [source.count("\n", 0, start) + 1,
                                 source.count("\n", 0, end) + 1],
                "source_function_sha256": digest(body),
            })
    if len(cases) != 151 or len({case["name"] for case in cases}) != 151:
        raise ValueError("expected exactly 151 distinct benchmark calls")
    return cases


def substitute_once(pattern: str, text: str, replacement: str = "") -> str:
    text, count = re.subn(pattern, replacement, text)
    if count != 1:
        raise ValueError(f"expected one scaffold match for {pattern!r}, got {count}")
    return text


def integerize(text: str) -> str:
    text = re.sub(r"\bTYPE\b", "int", text)
    return re.sub(r"\b(\d+)\.0*(?![\w.])", r"\1", text)


def helper_sources(source: str) -> dict[str, str]:
    """Read only known leaf helpers, including static-inline definitions."""
    clean = without_comments(source)
    result = {}
    for name, rule in HELPERS.items():
        match = re.search(rf"^(?:(?:static|inline)\s+)*(?:int|TYPE)\s+{name}\([^;{{}}]*\)\s*\{{", clean, re.M)
        if not match:
            raise ValueError(f"missing reviewed helper: {name}")
        end = closing_brace(clean, match.end() - 1)
        function = source[match.start():end]
        header = without_comments(function[:function.index("{")])
        if re.sub(r"\s", "", header) != re.sub(r"\s", "", rule.source_signature):
            raise ValueError(f"unreviewed helper interface: {name}")
        body = without_comments(function[function.index("{"):])
        calls = set(re.findall(r"\b(\w+)\s*\(", body)) - {"for", "if", "while", "sizeof"}
        if calls:
            raise ValueError(f"helper {name} has unreviewed transitive calls: {calls}")
        result[name] = function
    return result


def emit_helpers(spec: KernelSpec, sources: dict[str, str], *, reference: bool = False) -> str:
    definitions = []
    for name in spec.helpers:
        rule = HELPERS[name]
        body = sources[name][sources[name].index("{"):]
        parameters = list(rule.parameters)
        target_name = name if reference else f"tsvc_{name}"
        if not reference:
            body = integerize(without_comments(body))
            body = re.sub(r"\bLEN\b", "n", body)
            if rule.needs_n:
                parameters.append("int n")
            elif re.search(r"\bn\b", body):
                raise ValueError(f"helper {name} needs an unreviewed size parameter")
        definitions.append(f"static int {target_name}({', '.join(parameters) or 'void'}) " + body)
    if spec.integer_abs and not reference:
        definitions.append("static int tsvc_abs(int value) { return value < 0 ? -value : value; }")
    return "\n\n".join(definitions)


def adapt_special_computation(computation: str, spec: KernelSpec) -> str:
    """Only explicitly reviewed numeric/control adaptations, never broad folding."""
    for literal in spec.fractional_casts:
        computation = substitute_once(r"\(\s*TYPE\s*\)\s*" + re.escape(literal) + r"(?![\w.])",
                                      computation, "(TYPE)0")
    if spec.double_trig:
        block = re.search(r"#ifdef USE_FLOAT_TRIG\b.*?#endif", computation, re.S)
        expected = "#ifdef USE_FLOAT_TRIG a[i] = sinf(b[i]) + cosf(c[i]); #else a[i] = sin(b[i]) + cos(c[i]); #endif"
        if not block or re.sub(r"\s", "", block[0]) != re.sub(r"\s", "", expected):
            raise ValueError("unreviewed trig branch")
        computation = computation[:block.start()] + "a[i] = sin(b[i]) + cos(c[i]);" + computation[block.end():]
    if spec.termination:
        guard = r"if\s*\(d\[i\]\s*<\s*\(TYPE\)0\.\)\s*\{\s*exit\s*\(\s*0\s*\);\s*\}"
        if len(re.findall(guard, computation)) != 1:
            raise ValueError("unreviewed termination guard")
        computation = substitute_once(r"\bexit\s*\(\s*0\s*\);", computation, "return i;")
    return computation


def lower_helper_calls(computation: str, spec: KernelSpec) -> tuple[str, set[str]]:
    arrays = set()
    for name in spec.helpers:
        rule = HELPERS[name]

        def replace(match: re.Match) -> str:
            args = [argument.strip() for argument in match[1].split(",")] if match[1].strip() else []
            if len(args) != len(rule.parameters):
                raise ValueError(f"helper {name} argument mismatch")
            for position in rule.array_arguments:
                array = re.fullmatch(r"&?(\w+)(?:\[[^\[\]]+\])?", args[position])
                if not array:
                    raise ValueError(f"unreviewed helper array argument: {args[position]}")
                arrays.add(array[1])
            if rule.needs_n:
                args.append("n")
            return f"tsvc_{name}({', '.join(args)})"

        computation, count = re.subn(rf"\b{name}\s*\(([^()]*)\)", replace, computation)
        if not count:
            raise ValueError(f"reviewed helper {name} is not called")
    if spec.integer_abs:
        computation, count = re.subn(r"\bFABS\s*\(", "tsvc_abs(", computation)
        if not count:
            raise ValueError("reviewed absolute value is not used")
    calls = set(re.findall(r"\b(\w+)\s*\(", computation))
    allowed = {"for", "if", "while", "switch", "sizeof"} | {f"tsvc_{name}" for name in spec.helpers}
    if spec.integer_abs:
        allowed.add("tsvc_abs")
    if spec.double_trig:
        allowed.update(("sin", "cos"))
    if calls - allowed:
        raise ValueError(f"unreviewed computation calls: {calls - allowed}")
    return computation, arrays


def parameter_list(spec: KernelSpec, prefix: str = "") -> str:
    params = [f'{"const " if mode == "read" else ""}int *{prefix}{name}'
              for name, mode in spec.arrays.items()]
    params += [f"int *{prefix}out_{name}" for name in spec.outputs]
    params += [f"int {prefix}{name}" for name in spec.scalars]
    params.append(f"int {prefix}n")
    if spec.matrices:
        params.append(f"int {prefix}ld")
    return ", ".join(params)


def signature(name: str, spec: KernelSpec) -> str:
    return f"{spec.return_type} {name}({parameter_list(spec)})"


def bracket_end(text: str, start: int) -> int:
    """Return the end of a balanced subscript in comment-free computation."""
    depth = 0
    for pos in range(start, len(text)):
        if text[pos] == "[":
            depth += 1
        elif text[pos] == "]":
            depth -= 1
            if depth == 0:
                return pos + 1
    raise ValueError("unbalanced array subscript")


def check_subscript(index: str, spec: KernelSpec) -> None:
    def arithmetic(expression: str) -> None:
        if (not re.fullmatch(r"[\w\s()+*/-]+", expression) or "++" in expression or "--" in expression
                or re.search(r"\b[A-Za-z_]\w*\s*\(", expression)):
            raise ValueError(f"unsupported matrix subscript: {index}")

    def index_load(match: re.Match) -> str:
        if match[1] not in spec.index_arrays.split():
            raise ValueError(f"unreviewed index array: {match[1]}")
        arithmetic(match[2])
        return "index_value"

    # Permit a single level of loads from explicitly reviewed index arrays, not
    # arbitrary nested array expressions, calls, or side effects.
    simplified = re.sub(r"\b(\w+)\s*\[([^\[\]]+)\]", index_load, index)
    arithmetic(simplified)


def flatten_matrices(computation: str, spec: KernelSpec) -> str:
    """Lower reviewed two-subscript accesses, retaining permitted index loads."""
    seen, replacements = set(), []
    position = 0
    access = re.compile(r"\b(\w+)\s*\[")
    while match := access.search(computation, position):
        start = match.end() - 1
        first_end = bracket_end(computation, start)
        second_start = first_end
        while second_start < len(computation) and computation[second_start].isspace():
            second_start += 1
        if second_start == len(computation) or computation[second_start] != "[":
            if match[1] in spec.matrices.split():
                raise ValueError("matrix must have two subscripts")
            position = first_end
            continue
        end = bracket_end(computation, second_start)
        name = match[1]
        if name not in spec.matrices.split():
            raise ValueError(f"unreviewed matrix access: {name}")
        row, column = computation[start + 1:first_end - 1], computation[second_start + 1:end - 1]
        if spec.single_row_matrix and row.strip() != "0":
            raise ValueError("single-row access must use row zero")
        for index in (row, column):
            check_subscript(index, spec)
        replacements.append((match.start(), end, f"{name}[(size_t)({row.strip()}) * ld + ({column.strip()})]"))
        seen.add(name)
        position = end
    result = computation
    for start, end, replacement in reversed(replacements):
        result = result[:start] + replacement + result[end:]
    if re.search(r"\]\s*\[", result) or seen != set(spec.matrices.split()):
        raise ValueError("matrix accesses do not match the reviewed layouts")
    return result


def verify_original_parameters(clean: str, spec: KernelSpec) -> None:
    arguments = clean[clean.index("(") + 1:clean.index(")")].strip()
    actual = []
    for argument in arguments.split(",") if arguments else []:
        match = re.fullmatch(r"\s*(int|TYPE)\b\s*(?:(\*)\s*(?:__restrict__\s+)?)?(\w+)\s*", argument)
        if not match or (match[2] and match[1] != "int"):
            raise ValueError(f"unsupported original parameter: {argument}")
        actual.append((match[3], bool(match[2])))
    expected = [(name, True) for name in spec.pointer_params] + [(name, False) for name in spec.scalars]
    if actual != expected:
        raise ValueError(f"original parameter interface mismatch: {actual} versus {expected}")


def adjust_views(text: str, spec: KernelSpec, *, reference: bool = False) -> str:
    """Localize reviewed derived pointers without changing their address math."""
    declarations = []
    for name, value in spec.constants:
        if len(re.findall(rf"\bint\s+{name}\s*=\s*{value}\s*;", text)) != 1:
            raise ValueError(f"unreviewed pointer setup constant: {name}")
    for view in spec.views:
        if text.count(view.binding) != 1:
            raise ValueError(f"unreviewed pointer binding: {view.name}")
        type_ = "const int" if view.access == "read" else "int"
        if view.declaration:
            initializer = view.binding.split("=", 1)[1].strip()
            text = text.replace(view.binding, f"{type_} *{view.name} = {initializer}")
        elif not reference:
            declarations.append(f"{type_} *{view.name};")
    if declarations:
        text = "\n".join(declarations) + "\n" + text
    return text


def extract_computation(function: str, spec: KernelSpec) -> str:
    """Remove only recognized scaffolding, retaining all computational setup."""
    clean = without_comments(function)
    repetitions = list(REPETITION.finditer(clean))
    if len(repetitions) != 1 or "ntimes" not in repetitions[0][1]:
        raise ValueError("expected a single ntimes repetition loop")
    repetition = repetitions[0]
    end = closing_brace(clean, repetition.end() - 1)
    prelude = clean[clean.index("{") + 1:repetition.start()]
    for pattern in (
        r"clock_t\s+start_t,\s*end_t,\s*clock_dif;",
        r"double\s+clock_dif_sec;",
        r'init\s*\(\s*"[^"\n]*"\s*\);',
    ):
        prelude = substitute_once(pattern, prelude)
    prelude, clock_calls = re.subn(r"start_t\s*=\s*clock\(\);", "", prelude)
    if clock_calls != spec.start_clock_calls:
        raise ValueError("unexpected number of start-clock scaffold calls")
    for initializer in spec.remove_initializers:
        prelude = substitute_once(re.escape(initializer), prelude)

    body = clean[repetition.end():end - 1]
    dummy = re.search(r"\bdummy\([^;]*\);", body)
    if not dummy or body[dummy.end():].strip():
        raise ValueError("expected dummy() at the end of the repetition")
    if spec.result or spec.dummy_result:
        observation = spec.dummy_result or (r"[01](?:\.0*)?" if spec.postlude else
                      spec.result if spec.result_source == "dummy" else rf"(?:{spec.result}|0(?:\.0*)?)")
        if not re.search(rf",\s*{observation}\s*\);\Z", dummy.group()):
            raise ValueError("reviewed scalar output does not match dummy argument")
    elif not re.search(r",\s*[01](?:\.0*)?\s*\);\Z", dummy.group()):
        raise ValueError("unexposed dummy observation; review an explicit scalar output")
    body = substitute_once(r"\bdummy\([^;]*\);", body)

    # No other computation may silently disappear with the benchmark epilogue.
    tail = clean[end:clean.rfind("}")]
    for pattern in (
        r"end_t\s*=\s*clock\(\);",
        r"clock_dif\s*=\s*end_t\s*-\s*start_t;",
        r"clock_dif_sec\s*=\s*\(double\)\s*\(clock_dif\s*/\s*1000000\.0\);",
        r'printf\("(?:\\.|[^"\\])*"\s*,\s*clock_dif_sec\);',
        r"check\(-?\d+\);",
        r"return\s+0;",
    ):
        tail = substitute_once(pattern, tail)
    postlude = ""
    if spec.postlude:
        # Keep computational post-loop work only after an exact recipe check.
        # Ignore whitespace and extraneous empty statements at the outer edges,
        # not punctuation/order within the reviewed computation.
        compact = lambda text: re.sub(r"\s", "", text).strip(";")
        if compact(tail) != compact(spec.postlude):
            raise ValueError(f"unreviewed post-loop computation: {tail}")
        postlude = re.sub(r"\btemp\b", spec.result, tail.strip().lstrip(";").strip())
        postlude = textwrap.dedent(postlude.expandtabs(4)).strip() + "\n"
    else:
        tail = re.sub(r"[\s;]", "", tail)
        expected_tail = f"temp={spec.return_expression}" if spec.result_source == "temp" else ""
        if tail != re.sub(r"\s", "", expected_tail):
            raise ValueError(f"unreviewed post-loop computation: {tail}")

    prelude = textwrap.dedent(prelude.expandtabs(4)).strip()
    body = textwrap.dedent(body.expandtabs(4)).strip()
    computation = (prelude + "\n" if prelude else "") + "{\n" + textwrap.indent(body, "    ") + "\n}\n"
    for key in spec.outputs:
        computation += f"*out_{key} = {key};\n"
    if postlude:
        computation = f"int {spec.result};\n" + computation + postlude
    if spec.result:
        computation += f"return {spec.return_expression};\n"
    computation = adjust_views(computation, spec)
    if spec.matrices:
        if spec.single_row_matrix:
            if re.search(r"\bLEN2\b", computation) or not re.search(r"\bLEN\b", computation):
                raise ValueError("single-row matrix requires the reviewed LEN-only column domain")
            computation = re.sub(r"\b(?:LEN|lll)\b", "n", computation)
        else:
            if re.search(r"\b(?:LEN|lll)\b", computation):
                raise ValueError("mixed LEN/LEN2 extents require a separate review")
            computation = re.sub(r"\bLEN2\b", "n", computation)
        computation = flatten_matrices(computation, spec)
    else:
        computation = re.sub(r"\b(?:LEN|lll)\b", "n", computation)
    computation = adapt_special_computation(computation, spec)
    computation = integerize(computation)
    computation, helper_arrays = lower_helper_calls(computation, spec)
    if not re.search(r"\bn\b", computation):
        computation = "(void)n;\n" + computation
    if re.search(r"\b(?:LEN2|ntimes|dummy|temp|clock|init|check)\b|\d\.|\.\d|#", computation):
        raise ValueError("unsupported construct remains in computation")
    arrays = set(re.findall(r"\b(\w+)\s*\[", computation)) | helper_arrays
    view_bases = {view.name: view.base for view in spec.views}
    arrays = {view_bases.get(key, key) for key in arrays} | set(view_bases.values())
    if arrays != set(spec.arrays):
        raise ValueError(f"array interface mismatch: {arrays} versus {set(spec.arrays)}")
    verify_original_parameters(clean, spec)
    lines = computation.expandtabs(4).splitlines()
    # Original indentation is retained within the one-repetition block; remove
    # blank/comment-only lines without altering expressions or control flow.
    return "\n".join(line.rstrip() for line in lines if line.strip()).strip()


def array_contract(name: str, mode: str, spec: KernelSpec) -> dict:
    layout = spec.layout(name)
    extents = {"vector": "max(1, n)", "row_major_matrix": "max(1, n*ld)",
               "flat_square": "max(1, n*n)"}
    result = {"name": name, "access": mode, "layout": layout, "initialized": True}
    if layout == "offset_vector":
        offset = dict(spec.offset_vectors)[name]
        extent = f"max(0,{offset})" if name in spec.clamped_offsets.split() else offset
        result.update(offset_parameter=offset, minimum_elements=f"max(1, n+{extent})")
        if name in spec.clamped_offsets.split():
            result["clamp_negative_offset"] = True
    elif layout == "extended_vector":
        extra = dict(spec.extra_elements)[name]
        result.update(extra_elements=extra, minimum_elements=f"max(1, n+{extra})")
    elif layout == "strided_vector":
        stride = dict(spec.strided_vectors)[name]
        result.update(stride_parameter=stride, minimum_elements=f"max(1, n*{stride})",
                      padding="Stride gaps and unused trailing elements are preserved; stride zero aliases a single element.")
    else:
        result["minimum_elements"] = extents[layout]
    if layout == "row_major_matrix" and spec.single_row_matrix:
        result.update(minimum_elements="max(1, ld)", logical_rows=1, logical_columns="n")
    if layout in ("extended_vector", "strided_vector", "offset_vector"):
        result["allocation"] = "The mathematical required element count times sizeof(int) must fit SIZE_MAX and the supplied allocation."
    if name in spec.selector_arrays.split():
        result["selector_domain"] = {"values": "any signed 32-bit int", "cases": [1, 2, 3, 4],
                                     "default": "fall through to case 1"}
    if name in spec.exclude_int_min.split():
        result["value_domain"] = {"minimum": -2147483647, "maximum": 2147483647,
                                  "reason": "INT_MIN has no representable positive int magnitude"}
    if name in spec.index_arrays.split():
        result["index_domain"] = {"positions": "0 <= i < n", "minimum": 0,
                                  "maximum_exclusive": "n", "duplicates_allowed": True,
                                  "ordering": "arbitrary; preserve scalar execution/store order"}
    return result


def scalar_contract(name: str, spec: KernelSpec) -> dict:
    result = {"name": name, "type": "int"}
    domain = dict(spec.scalar_domains).get(name)
    if domain:
        result["domain"] = {"id": domain, **SCALAR_DOMAINS[domain]}
    return result


def contract(spec: KernelSpec) -> dict:
    result = {
        "integer_type": "signed 32-bit int",
        "execution": "One execution of the original repetition-loop body, including local setup.",
        "size": {"parameter": "n", "minimum": spec.minimum_n,
                 "maximum": MAX_MATRIX_N if spec.matrices and not spec.single_row_matrix else MAX_N, "multiple_of": spec.n_multiple},
        "arrays": [array_contract(name, mode, spec) for name, mode in spec.arrays.items()],
        "scalar_inputs": [scalar_contract(name, spec) for name in spec.scalars],
        "scalar_output": {"type": "int", "source_variable": spec.result,
                          "observation": spec.result_source} if spec.result else None,
        "aliasing": "Distinct array arguments must have non-overlapping storage, matching the original globals. No restrict qualifier is added.",
        "arithmetic": "Every evaluated signed arithmetic expression must be representable as int. Signed overflow is not defined as wraparound.",
        "memory": "All array arguments are valid initialized buffers, also when n=0. No alignment beyond int alignment is required.",
        "empty_input": spec.empty_input or ("Not admitted by the size contract." if spec.minimum_n else "No array writes; reductions return 0."),
        "notes": spec.note,
    }
    if spec.excluded_n:
        result["size"]["excluded"] = list(spec.excluded_n)
    if spec.fractional_casts:
        result["numeric_adaptation"] = {
            "kind": "degenerate_fractional_cast", "pure_integer": True,
            "casts": [{"source": f"(TYPE){value}", "integer_value": 0} for value in spec.fractional_casts],
            "warning": "Integer casts truncate these fractions to zero; this is not floating-point scaling. Evaluated sums must still fit int.",
        }
    if spec.double_trig:
        result["numeric_adaptation"] = {
            "kind": "integer_storage_double_libm", "pure_integer": False,
            "branch": "sin/cos, not sinf/cosf", "input_conversion": "exact int32 to binary64",
            "output_conversion": "truncate the double sum toward zero to int, not each term separately",
            "environment": "same conforming libm and default floating-point environment; no fast-math; errno and floating-point exception flags are outside the observable interface",
            "link_libraries": ["m"],
        }
    if spec.termination:
        result["termination"] = {"source": "exit(0)", "process_termination": False,
                                 "return_on_stop": "zero-based index of the first negative d element, before its update",
                                 "return_on_completion": -1, "preserved_state": "updated prefix and untouched stop element/suffix"}
        result["scalar_output"].update(source_variable=None, meaning="stop index, or -1 on completion")
    result["scalar_outputs"] = [{"parameter": f"out_{key}", "source_variable": key,
                                  "type": "int", "access": "write", "minimum_elements": 1,
                                  "initialized": True} for key in spec.outputs]
    if spec.result_expression:
        result["scalar_output"].update(source_variable=None, source_expression=spec.result_expression)
    if spec.postlude:
        result["scalar_output"].update(source_variable="temp", kernel_variable=spec.result,
                                       source_computation=spec.postlude)
        result["execution"] += " Retain the explicitly reviewed post-loop computation."
    if spec.remove_initializers:
        result["removed_benchmark_initializers"] = list(spec.remove_initializers)
    if spec.views:
        result["pointer_views"] = [{"name": view.name, "base": view.base,
                                    "initial_offset_elements": view.offset, "access": view.access,
                                    "binding": view.binding, "induction": view.declaration}
                                   for view in spec.views]
        result["aliasing"] += " Derived pointer views share their base buffer, may overlap it, and are not restrict-qualified."
    if spec.outputs:
        result["dummy_observation"] = spec.dummy_result
        result["aliasing"] += " Scalar output slots are pairwise disjoint and disjoint from every array."
    if spec.matrices:
        result["row_stride"] = {
            "parameter": "ld", "minimum": "max(1, n)", "maximum": 2147483647,
            "unit": "int elements", "shared_by": spec.matrices.split(),
            "logical_shape": "n by n (square)",
            "padding": "Columns [n, ld) of each row are preserved.",
            "allocation": "The mathematical n*ld*sizeof(int) must fit in SIZE_MAX and in the supplied allocation.",
        }
        if spec.single_row_matrix:
            result["row_stride"].update(logical_shape="1 by n (single row)",
                                       allocation="The mathematical ld*sizeof(int) must fit in SIZE_MAX and in the supplied allocation.")
            result["extent_adaptation"] = "Supply one valid row of n columns; do not reproduce cross-row aa[0][i] accesses when original LEN exceeds LEN2."
    return result


def emit_kernel(name: str, function: str, spec: KernelSpec, helpers: dict[str, str] | None = None) -> str:
    body = extract_computation(function, spec)
    arrays = ", ".join(f"{key}: {value}" for key, value in spec.arrays.items()) or "none"
    bound = MAX_MATRIX_N if spec.matrices and not spec.single_row_matrix else MAX_N
    layout_note = ("Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).\n"
                   " * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved."
                   if spec.matrices else "Each has at least max(1,n) initialized ints.")
    allocation_note = "\n * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation." if spec.matrices else ""
    if spec.single_row_matrix:
        layout_note = "Matrices are single rows: ld >= max(1,n), with ld initialized ints. Vectors use max(1,n)."
        allocation_note = "\n * ld*sizeof(int) must fit in SIZE_MAX; row padding is preserved. No cross-row access."
    if spec.excluded_n:
        allocation_note += f"\n * Excluded sizes: {', '.join(map(str, spec.excluded_n))}."
    if spec.fractional_casts:
        allocation_note += "\n * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation)."
    if spec.double_trig:
        allocation_note += "\n * Mixed numeric computation: double sin/cos and addition, then truncate to int; link libm, no fast-math."
    if spec.termination:
        allocation_note += "\n * Return first negative d index before its update, or -1 on completion; never terminate the process."
    if spec.n_multiple != 1:
        allocation_note += f"\n * n must be divisible by {spec.n_multiple}, as required by the original unrolled loop."
    for key, offset in spec.offset_vectors:
        extent = f"max(0,{offset})" if key in spec.clamped_offsets.split() else offset
        allocation_note += f"\n * {key} instead requires max(1,n+{extent}) initialized ints."
    for key in (*dict(spec.extra_elements), *dict(spec.strided_vectors)):
        extent = array_contract(key, spec.arrays[key], spec)["minimum_elements"]
        allocation_note += f"\n * {key} instead requires {extent} initialized ints; allocation bytes must fit SIZE_MAX."
    for view in spec.views:
        allocation_note += f"\n * {view.name} initially aliases {view.base}+({view.offset}) ints; not an independent buffer."
    for key in spec.index_arrays.split():
        allocation_note += f"\n * For 0 <= i < n: 0 <= {key}[i] < n. Duplicates are allowed; preserve store order."
    for key in spec.selector_arrays.split():
        allocation_note += f"\n * {key} selectors may be any int; values outside 1..4 use the case-1 computation."
    for key, domain in spec.scalar_domains:
        bounds = SCALAR_DOMAINS[domain]
        allocation_note += f"\n * Scalar contract: {bounds['minimum']} <= {key} <= {bounds['maximum']}."
    if spec.outputs:
        allocation_note += "\n * Scalar output pointers each address one initialized int, disjoint from all other buffers."
    for key in spec.exclude_int_min.split():
        allocation_note += f"\n * No element of {key} may equal INT_MIN (integer absolute-value contract)."
    comment = f"""/* TSVC integer adaptation: {name} (one computational repetition).
 * Contract: {spec.minimum_n} <= n <= {bound}; no SIMD-width divisibility requirement.
 * Arrays: {arrays}. {layout_note}{allocation_note}
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/{name}.json for the complete contract and adaptations.
 * Source SHA256: {digest(function)}
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
"""
    if spec.matrices:
        comment += "#include <stddef.h>\n"
    if spec.double_trig:
        comment += "#include <math.h>\n#include <float.h>\n"
        comment += "_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024 && FLT_EVAL_METHOD == 0, \"Requires binary64 evaluation\");\n"
        comment += "#ifdef __FAST_MATH__\n#error \"s451 requires strict math\"\n#endif\n"
    helper_code = emit_helpers(spec, helpers or {})
    if helper_code:
        comment += "\n" + helper_code + "\n"
    return comment + "\n" + signature(name, spec) + " {\n" + textwrap.indent(body, "    ") + "\n}\n"


def emit_reference(name: str, function: str, spec: KernelSpec, helpers: dict[str, str] | None = None) -> str:
    """Keep the original function, independently of extract_computation()."""
    original = substitute_once(rf"\b{name}\s*\(", function, f"original_{name}(")
    original = substitute_once(REPETITION.pattern, original, "for (int nl = 0; nl < 1; nl++) {")
    for initializer in spec.remove_initializers:
        original = substitute_once(re.escape(initializer), original, "/* Initialization is supplied by the caller. */")
    original = adjust_views(original, spec, reference=True)

    def storage(key: str) -> str:
        return f"reference_storage_{key}" if key in spec.matrices.split() else key

    globals_ = "\n".join(
        f'static {"const " if mode == "read" else ""}int *{storage(key)};'
        for key, mode in spec.arrays.items() if key not in spec.pointer_params
    )
    for view in spec.views:
        if not view.declaration:
            globals_ += f'\nstatic {"const " if view.access == "read" else ""}int *{view.name};'
    bindings = "\n".join(f"    {storage(key)} = arg_{key};" for key in spec.arrays if key not in spec.pointer_params)
    # The original functions take int* (sometimes restrict). They only read the
    # reviewed index inputs; the wrapper exposes const without rewriting bodies.
    original_args = [f"(int *)arg_{key}" for key in spec.pointer_params] + [f"arg_{key}" for key in spec.scalars]
    if spec.matrices:
        # The oracle keeps aa[i][j] with a pointer-to-VLA local alias, rather
        # than using the flattened address expressions emitted for the kernel.
        aliases = []
        for key in spec.matrices.split():
            type_ = "const int" if spec.arrays[key] == "read" else "int"
            aliases.append(f"    {type_} (*{key})[reference_ld] = ({type_} (*)[reference_ld]){storage(key)};")
        old_params = re.search(rf"int original_{name}\(([^)]*)\)", original)[1].strip()
        params = ", ".join(([old_params] if old_params else []) + ["int reference_ld"])
        original = substitute_once(rf"int original_{name}\([^)]*\)\s*\{{", original,
                                   f"int original_{name}({params}) {{\n" + "\n".join(aliases))
        original_args.append("arg_ld")
    scalar_args = ", ".join(original_args)
    dimension_define = "#define LEN2 reference_n\n" if spec.matrices and not spec.single_row_matrix else ""
    observation = "temp" if spec.result_source in ("temp", "postlude") else "reference_last_scalar"
    if spec.termination:
        observation = "reference_stop_index"
        globals_ += "\nstatic int reference_stop_index;\n#define exit(status) do { reference_stop_index = i; return 0; } while (0)"
    result = "".join(f"    *arg_out_{key} = reference_output_{key};\n" for key in spec.outputs)
    result += f"    return {observation};\n" if spec.result else ""
    dummy_macro = "#define dummy(a,b,c,d,e,aa,bb,cc,value) (reference_last_scalar = (value))"
    if spec.outputs:
        captures = ", ".join(f"reference_output_{key} = ({key})" for key in spec.outputs)
        dummy_macro = f"#define dummy(_a,_b,_c,_d,_e,_aa,_bb,_cc,_scalar) (reference_last_scalar = (_scalar), {captures})"
        globals_ += "\n" + "\n".join(f"static int reference_output_{key};" for key in spec.outputs)
    support = emit_helpers(spec, helpers or {}, reference=True)
    if spec.integer_abs:
        support = "#define FABS(value) abs(value)\n" + support
    if support:
        globals_ += "\n\n" + support
    extra_include = "#include <stdlib.h>\n" if spec.integer_abs else ""
    if spec.double_trig:
        extra_include += "#include <math.h>\n#undef USE_FLOAT_TRIG\n"
    reset_outcome = "    reference_stop_index = -1;\n" if spec.termination else ""
    return f"""/* TEST ONLY: original {name} with its harness disabled, not the extracted kernel.
 * Retains the original global names, declarations, computational statements and
 * epilogue. LEN/LEN2 are bound at runtime; nl executes exactly once.
 * Do not send this file to the LLM or use it for performance measurement.
 */
#include <time.h>
{extra_include}#define TYPE int
#define LEN reference_n
#define lll LEN
{dimension_define}#define clock() ((clock_t)0)
#define init(...) ((void)0)
#define check(...) ((void)0)
#define printf(...) ((void)0)
{dummy_macro}
static int reference_n;
static int reference_last_scalar;
static int temp;
{globals_}

{original}

{spec.return_type} reference_{name}({parameter_list(spec, "arg_")}) {{
    reference_n = arg_n;
    reference_last_scalar = 0;
{reset_outcome}{bindings}
    original_{name}({scalar_args});
{result}}}
"""


def review_reason(category: str, function: str) -> str:
    if category == "EQUIVALENCING":
        return "Review pointer offsets, storage overlap, and alias relationships."
    if category == "INDIRECT_ADDRESSING" or re.search(r"\bip\s*\[", function):
        return "Review indirect index domains and scatter/gather dependencies."
    if "LEN2" in function:
        return "Review 2D dimensions, row stride, and relationships to 1D extents."
    if category == "REDUCTIONS":
        return "Review scalar outputs, reduction arithmetic, and empty-input behavior."
    return "Review interface, local/global state, helpers, bounds, and integer arithmetic."


def generate(source_path: Path, output: Path) -> dict:
    # Check bytes, not newline-normalized text: provenance is exact.
    raw = source_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REVIEWED_SOURCE_SHA256:
        raise ValueError("TSVC source differs from the reviewed snapshot; review changes before updating the hash")
    source = raw.decode()
    cases = inventory(source)
    funcs = functions(source)
    helpers = helper_sources(source)
    if set(SPECS) - {case["name"] for case in cases}:
        raise ValueError("a reviewed case is missing from the inventory")
    files = {}
    prototypes = []
    for case in cases:
        name = case["name"]
        function = funcs[name][2]
        if name not in SPECS:
            case.update(status="needs_review", reason=DEFERRED_REASONS.get(name, review_reason(case["category"], function)))
            continue
        spec = SPECS[name]
        case.update(status="generated", signature=signature(name, spec),
                    kernel=f"kernels/{name}.c", reference=f"reference/{name}.c",
                    contract=contract(spec),
                    adaptations=["float/double data type -> signed int",
                                 "remove harness and execute one computational repetition",
                                 "LEN2 -> runtime n" if spec.matrices and not spec.single_row_matrix else "LEN/lll -> runtime n",
                                 "integral floating literals -> integer literals"])
        if spec.matrices:
            case["adaptations"].append("single-row LEN-column matrix with explicit ld; no out-of-row reads" if spec.single_row_matrix else
                                       "square matrices -> flat row-major buffers with explicit shared ld; packed arrays stay contiguous")
        caveats = []
        if spec.fractional_casts:
            caveats.append("degenerate_fractional_cast")
            case["adaptations"].append("explicitly reviewed fractional TYPE casts -> integer zero; not fixed-point arithmetic or division")
        if spec.double_trig:
            caveats.append("mixed_double_libm")
            case["adaptations"].append("select double sin/cos branch; integer storage with double intermediate sum and final int truncation")
        if spec.termination:
            caveats.append("process_exit_to_returned_outcome")
            case["adaptations"].append("replace process exit(0) with an observable stop index; -1 means completed")
        if spec.single_row_matrix:
            caveats.append("single_row_extent_generalization")
        if caveats:
            case["experiment_caveats"] = {"flags": caveats, "aggregate_policy": "report separately; do not silently pool with ordinary integer kernels"}
        if spec.index_arrays:
            case["adaptations"].append("explicit read-only index buffers; bounded but not assumed unique")
        if spec.result:
            case["adaptations"].append(f"expose {spec.result_source}'s scalar observation as the return value")
        if spec.views:
            case["adaptations"].append("one backing buffer per storage object; preserve derived pointer aliases and induction without restrict")
        if spec.remove_initializers:
            case["adaptations"].append("remove only the explicitly reviewed benchmark initialization; caller supplies the initial state")
        if spec.postlude:
            case["adaptations"].append("retain reviewed post-loop summation; replace global temp by a returned local checksum")
        if spec.outputs:
            case["adaptations"].append("expose reviewed local scalar state and dummy observation in disjoint output slots")
        if spec.integer_abs:
            case["adaptations"].append("FABS -> integer absolute value, excluding INT_MIN")
        if spec.helpers:
            case["adaptations"].append("include reviewed leaf helpers; explicit size where needed, const read-only pointers, no VLA parameter bounds")
        case["helpers"] = [{"name": key, "source_sha256": digest(helpers[key])} for key in spec.helpers]
        case["testing"] = {"profile": spec.test_profile, "description": TEST_PROFILES[spec.test_profile],
                           "contract_restriction": False}
        files[case["kernel"]] = emit_kernel(name, function, spec, helpers)
        files[case["reference"]] = emit_reference(name, function, spec, helpers)
        files[f"contracts/{name}.json"] = json.dumps(case, indent=2) + "\n"
        prototypes.append(signature(name, spec) + ";")
    manifest = {
        "schema_version": 6,
        "dataset": "TSVC-151-parameterized-int",
        "source": "llvm-test-suite/MultiSource/Benchmarks/TSVC/tsc.inc",
        "source_sha256": REVIEWED_SOURCE_SHA256,
        "generated_count": len(SPECS),
        "needs_review_count": len(cases) - len(SPECS),
        "validation_status": "not_run; use check_tsvc_kernels.py and retain its report",
        "cases": cases,
    }
    files["manifest.json"] = json.dumps(manifest, indent=2) + "\n"
    files["kernels.h"] = ("#ifndef TSVC_INTEGER_KERNELS_H\n#define TSVC_INTEGER_KERNELS_H\n\n"
                          + "\n".join(prototypes) + "\n\n#endif\n")
    files["LICENSE.TXT"] = source_path.with_name("LICENSE.TXT").read_text()
    files["README.md"] = f"""# Parameterized integer TSVC kernels

{len(SPECS)} kernels are emitted; all 151 benchmark cases appear in `manifest.json`.
Cases marked `needs_review` are not silently dropped or claimed as supported.
See `docs/tsvc-parameterization-plan.md` and `docs/tsvc-kernels.md` in the project.

- `kernels/`: self-contained C11 functions, no main or mutable global state.
- `contracts/`: per-case interface, bounds, assumptions, and source provenance.
- `kernels.h`: declarations for the generated interfaces.
- `reference/`: test-only adapters around original TSVC functions, not LLM inputs.
- `LICENSE.TXT`: upstream TSVC license; applies to copied/adapted source.

The kernel performs one computational repetition. It is an integer adaptation,
not equivalent to the original floating-point benchmark. It is not the paper's
149-function dataset. Generation is not testing or formal validation.
Reviewed post-loop observations are part of the kernel interface where listed.
Five fractional-cast cases are numerically degenerate. s451 uses integer storage
but double libm arithmetic; s481 returns a stop outcome instead of exiting the
process. s258/vbor require a valid single row rather than an out-of-row access.
These cases have explicit experiment_caveats and must be reported separately.

From the project root, run:

    python3 scripts/check_tsvc_kernels.py --directory /path/to/this/dataset --sanitize

The original whole-program files in `generated/tsvc-int` are unrelated outputs
and are not used as the testing oracle. In particular, their initializers and
checksums are not suitable as a correctness oracle for this adaptation.
"""
    # Validate every recipe before writing; do not mix old/stale kernels into a
    # new inventory or overwrite the user's candidate files.
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(f"output must be absent or empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    for path, content in files.items():
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=ROOT / "generated/tsvc-kernels")
    args = parser.parse_args()
    try:
        manifest = generate(args.source, args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Generated {manifest['generated_count']} kernels; "
          f"{manifest['needs_review_count']} need review. Inventory: {args.output / 'manifest.json'}")


if __name__ == "__main__":
    main()
