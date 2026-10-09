"""Regression tests for the reviewed TSVC parameterization batch."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# These are standalone command-line tools, not an installed Python package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_tsvc_kernels import (
    DEFAULT_MATRIX_SIZES, DEFAULT_SIZES, DEFAULT_STRIDE_PADDINGS, INDEX_PATTERNS,
    driver, eligible_sizes, run_checks,
)
from extract_tsvc_int import DEFAULT_SOURCE, functions
from generate_tsvc_kernels import (
    MAX_MATRIX_N, MAX_N, extract_computation, flatten_matrices, generate, inventory, without_comments,
)
from tsvc_kernel_specs import REVIEWED_SOURCE_SHA256, SPECS, KernelSpec


class LexingTests(unittest.TestCase):
    def test_comments_preserve_offsets_and_strings(self):
        source = 'int x; /* }\n // comment */ "not // a comment"; // {\n'
        masked = without_comments(source)
        self.assertEqual(len(source), len(masked))
        self.assertEqual(source.count("\n"), masked.count("\n"))
        self.assertIn('"not // a comment"', masked)
        self.assertNotIn("/*", masked)
        self.assertNotIn("{", masked)


@unittest.skipUnless(DEFAULT_SOURCE.exists(), "requires the reviewed llvm-test-suite checkout")
class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="tsvc-unit-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.output = cls.root / "dataset"
        cls.manifest = generate(DEFAULT_SOURCE, cls.output)
        cls.source = DEFAULT_SOURCE.read_text()
        cls.funcs = functions(cls.source)
        cls.cases = {case["name"]: case for case in cls.manifest["cases"]}

    def test_inventory_has_all_151_and_18_categories(self):
        cases = inventory(self.source)
        self.assertEqual(len(cases), 151)
        self.assertEqual(len({case["name"] for case in cases}), 151)
        self.assertEqual(len({case["category"] for case in cases}), 18)
        self.assertEqual(self.manifest["source_sha256"], REVIEWED_SOURCE_SHA256)
        self.assertEqual(self.manifest["generated_count"], 151)
        self.assertEqual(self.manifest["needs_review_count"], 0)
        self.assertEqual(self.manifest["schema_version"], 6)
        self.assertEqual(self.manifest["validation_status"].split(";")[0], "not_run")

    def test_duplicate_call_is_rejected(self):
        before, main = self.source.split("int main(", 1)
        changed = before + "int main(" + main.replace("s124();", "s124();\n s124();", 1)
        with self.assertRaisesRegex(ValueError, "151 distinct"):
            inventory(changed)

    def test_file_set_exactly_matches_reviewed_cases(self):
        for folder, extension in (("kernels", "c"), ("reference", "c"), ("contracts", "json")):
            self.assertEqual({file.stem for file in (self.output / folder).glob(f"*.{extension}")}, set(SPECS))
        for case in self.cases.values():
            if case["status"] == "needs_review":
                self.assertTrue(case["reason"])
                self.assertNotIn("kernel", case)
                self.assertNotIn("signature", case)
        self.assertEqual((self.output / "LICENSE.TXT").read_bytes(),
                         DEFAULT_SOURCE.with_name("LICENSE.TXT").read_bytes())

    def test_generation_is_deterministic(self):
        other = self.root / "repeat"
        generate(DEFAULT_SOURCE, other)
        for original in self.output.rglob("*"):
            if original.is_file():
                self.assertEqual(original.read_bytes(), (other / original.relative_to(self.output)).read_bytes())

    def test_refuses_overwrite_or_changed_source(self):
        with self.assertRaisesRegex(ValueError, "absent or empty"):
            generate(DEFAULT_SOURCE, self.output)
        changed = self.root / "changed.inc"
        changed.write_text(self.source.replace("j = -1;", "j = 0;", 1))
        destination = self.root / "should-not-exist"
        with self.assertRaisesRegex(ValueError, "reviewed snapshot"):
            generate(changed, destination)
        self.assertFalse(destination.exists())

    def test_contracts_have_explicit_inputs_and_semantics(self):
        for name in SPECS:
            case = self.cases[name]
            disk = json.loads((self.output / "contracts" / f"{name}.json").read_text())
            self.assertEqual(disk, case)
            c = case["contract"]
            bound = MAX_MATRIX_N if SPECS[name].matrices and not SPECS[name].single_row_matrix else MAX_N
            expected_size = {"parameter": "n", "minimum": SPECS[name].minimum_n,
                             "maximum": bound, "multiple_of": SPECS[name].n_multiple}
            if SPECS[name].excluded_n:
                expected_size["excluded"] = list(SPECS[name].excluded_n)
            self.assertEqual(c["size"], expected_size)
            self.assertIn("non-overlapping", c["aliasing"])
            self.assertIn("not defined as wraparound", c["arithmetic"])
            for array in c["arrays"]:
                layout = SPECS[name].layout(array["name"])
                self.assertEqual(array["layout"], layout)
                if layout == "offset_vector":
                    offset = dict(SPECS[name].offset_vectors)[array["name"]]
                    self.assertEqual(array["offset_parameter"], offset)
                    if array["name"] in SPECS[name].clamped_offsets.split():
                        self.assertTrue(array["clamp_negative_offset"])
                        offset = f"max(0,{offset})"
                    extent = f"max(1, n+{offset})"
                elif layout == "extended_vector":
                    extra = dict(SPECS[name].extra_elements)[array["name"]]
                    self.assertEqual(array["extra_elements"], extra)
                    extent = f"max(1, n+{extra})"
                elif layout == "strided_vector":
                    stride = dict(SPECS[name].strided_vectors)[array["name"]]
                    self.assertEqual(array["stride_parameter"], stride)
                    extent = f"max(1, n*{stride})"
                else:
                    extent = {"vector": "max(1, n)", "flat_square": "max(1, n*n)",
                              "row_major_matrix": "max(1, n*ld)"}[layout]
                if layout == "row_major_matrix" and SPECS[name].single_row_matrix:
                    self.assertEqual(array["logical_rows"], 1)
                    extent = "max(1, ld)"
                self.assertEqual(array["minimum_elements"], extent)
                self.assertTrue(array["initialized"])

    def test_s124_has_only_computation_and_preserves_setup(self):
        kernel = without_comments((self.output / "kernels/s124.c").read_text())
        self.assertIn("void s124(int *a, const int *b, const int *c, const int *d, const int *e, int n)", kernel)
        self.assertIn("int j;", kernel)
        self.assertIn("j = -1;", kernel)
        self.assertIn("i < n", kernel)
        self.assertIn("a[j] = b[i] + d[i] * e[i];", kernel)
        self.assertIn("a[j] = c[i] + d[i] * e[i];", kernel)
        self.assertNotRegex(kernel, r"\b(?:LEN|TYPE|ntimes|nl|init|check|clock|printf|dummy|restrict|main)\b")

    def test_offsets_reverse_iteration_gotos_and_odd_tails_are_preserved(self):
        expected = {
            "s112": "int i = n - 2; i >= 0; i--",
            "s116": "i < n - 5; i += 5",
            "s121": "i < n-1",
            "s127": "i < n/2",
            "s276": "int mid = (n/2);",
            "s278": "goto L20;",
        }
        for name, expression in expected.items():
            self.assertIn(expression, (self.output / f"kernels/{name}.c").read_text())

    def test_declarations_before_timer_and_scalar_interfaces(self):
        s453 = (self.output / "kernels/s453.c").read_text()
        self.assertIn("int s;", s453)
        self.assertIn("s = 0;", s453)
        self.assertIn("s += (int)2;", s453)
        self.assertIn("int t, int n)", self.cases["s272"]["signature"])
        self.assertIn("int s, int n)", self.cases["vpvts"]["signature"])
        for name, scalar in (("vsumr", "sum"), ("vdotr", "dot")):
            self.assertTrue(self.cases[name]["signature"].startswith(f"int {name}("))
            self.assertIn(f"return {scalar};", (self.output / f"kernels/{name}.c").read_text())

    def test_reference_uses_original_function_not_extracted_computation(self):
        reference = (self.output / "reference/s124.c").read_text()
        self.assertIn('init( "s124 ");', reference)
        self.assertIn("for (int nl = 0; nl < 1; nl++)", reference)
        self.assertIn("i < LEN", reference)
        self.assertIn("(TYPE)0.", reference)
        self.assertIn("reference_n = arg_n;", reference)
        self.assertIn("original_s124();", reference)

    def test_unknown_post_loop_work_cannot_be_dropped(self):
        original = self.funcs["s124"][2]
        modified = original.replace("end_t = clock();", "a[0] = 123;\nend_t = clock();")
        with self.assertRaisesRegex(ValueError, "unreviewed post-loop"):
            extract_computation(modified, SPECS["s124"])

    def test_runner_checks_const_inputs_and_reduction_return(self):
        code = driver([self.cases["s124"], self.cases["vsumr"]], [0, 7, 8, 9], 8, 42)
        self.assertIn('compare("s124", "e"', code)
        self.assertIn("got_result != want_result", code)
        self.assertIn("mode == 0 ? 0 : 16", code)

    def test_runner_rejects_invalid_selection_sizes_and_seed(self):
        for args in ({"names": ["not_a_case"]}, {"names": ["s124", "s124"]},
                     {"sizes": [-1]}, {"sizes": []}, {"seed": -1},
                     {"matrix_sizes": [-1]}, {"matrix_sizes": [129]}, {"matrix_sizes": []},
                     {"stride_paddings": [-1]}, {"stride_paddings": [65]}, {"stride_paddings": []},
                     {"names": ["s353"], "sizes": [1, 7, 9]}, {"names": ["s314"], "sizes": [0]},
                     {"candidate_dir": self.root}):
            with self.assertRaises(ValueError):
                run_checks(self.output, **args)

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_all_reviewed_cases_with_sanitizers(self):
        report = run_checks(self.output, cc="clang", sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))
        self.assertEqual(report["executions"], 144072)
        self.assertEqual(len(report["inputs"]), 151)
        self.assertEqual(len(report["matrix_cases"]), 29)
        self.assertEqual(report["single_row_cases"], ["s258", "vbor"])
        self.assertEqual(report["termination_cases"], ["s481"])
        self.assertEqual(report["link_libraries"], ["m"])
        self.assertEqual(len(report["experiment_caveats"]), 9)
        self.assertEqual(len(report["indexed_cases"]), 9)
        self.assertEqual(report["index_patterns"], INDEX_PATTERNS)
        self.assertEqual(report["tested_sizes"]["s353"], [0, 5, 10, 15, 40, 65])
        self.assertEqual(report["selector_cases"], ["s442"])
        self.assertEqual(len(report["pointer_view_cases"]), 6)
        self.assertEqual(report["excluded_sizes"]["s314"], [0])
        self.assertEqual(report["excluded_sizes"]["s316"], [0])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_incorrect_candidate_is_rejected(self):
        candidates = self.root / "bad-candidates"
        candidates.mkdir()
        # Same interface, but the true branch writes the wrong value. A checksum
        # or a zero-only smoke test could miss this; the full-state test must not.
        original = (self.output / "kernels/s124.c").read_text()
        candidates.joinpath("s124.c").write_text(original.replace("a[j] = b[i] + d[i] * e[i];", "a[j] = 0;"))
        report = run_checks(self.output, names=["s124"], candidate_dir=candidates,
                            sizes=[0, 1, 7, 8, 9], trials=8, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("s124: a[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_wrong_scalar_return_is_rejected(self):
        candidates = self.root / "bad-reduction"
        candidates.mkdir()
        original = (self.output / "kernels/vsumr.c").read_text()
        candidates.joinpath("vsumr.c").write_text(original.replace("return sum;", "return 0;"))
        report = run_checks(self.output, names=["vsumr"], candidate_dir=candidates,
                            sizes=[0, 1, 9], trials=8)
        self.assertEqual(report["status"], "failed")
        self.assertIn("vsumr: scalar", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_wrong_candidate_signature_is_compile_error(self):
        candidates = self.root / "bad-interface"
        candidates.mkdir()
        candidates.joinpath("vsumr.c").write_text("int vsumr(void) { return 0; }\n")
        report = run_checks(self.output, names=["vsumr"], candidate_dir=candidates)
        self.assertEqual(report["status"], "failed")
        self.assertIn("conflicting types", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_sanitizer_detects_out_of_bounds_candidate(self):
        candidates = self.root / "bad-bounds"
        candidates.mkdir()
        original = (self.output / "kernels/s124.c").read_text()
        candidates.joinpath("s124.c").write_text(original.replace("int j;", "a[n] = 0; int j;"))
        report = run_checks(self.output, names=["s124"], candidate_dir=candidates,
                            sizes=[1], trials=1, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("AddressSanitizer", report["error"])

    def test_matrix_layouts_have_independent_logical_and_physical_extents(self):
        for name, spec in SPECS.items():
            if not spec.matrices:
                continue
            case = self.cases[name]
            self.assertTrue(case["signature"].endswith("int n, int ld)"))
            self.assertEqual(case["contract"]["row_stride"]["minimum"], "max(1, n)")
            self.assertEqual(case["contract"]["row_stride"]["shared_by"], spec.matrices.split())
        packed = {array["name"]: array for array in self.cases["s125"]["contract"]["arrays"]}
        self.assertEqual(packed["array"]["minimum_elements"], "max(1, n*n)")
        self.assertEqual(packed["aa"]["minimum_elements"], "max(1, n*ld)")
        mixed = {array["name"]: array for array in self.cases["s235"]["contract"]["arrays"]}
        self.assertEqual(mixed["a"]["minimum_elements"], "max(1, n)")
        self.assertEqual(mixed["aa"]["layout"], "row_major_matrix")

    def test_reference_keeps_two_subscripts_instead_of_flattening(self):
        kernel = without_comments((self.output / "kernels/s114.c").read_text())
        reference = (self.output / "reference/s114.c").read_text()
        self.assertIn("aa[(size_t)(i) * ld + (j)] = aa[(size_t)(j) * ld + (i)]", kernel)
        self.assertIn("int (*aa)[reference_ld]", reference)
        self.assertIn("const int (*bb)[reference_ld]", reference)
        self.assertIn("aa[i][j] = aa[j][i] + bb[i][j];", reference)
        self.assertIn("original_s114(arg_ld);", reference)
        self.assertIn("#define LEN2 reference_n", reference)
        self.assertNotIn("* ld +", reference)

    def test_matrix_extractor_rejects_unreviewed_indexing_and_mixed_dimensions(self):
        for expression in ("aa[i++][j] + bb[i][j]", "aa[i][ip[j]] + bb[i][j]", "aa[f(i)][j] + bb[i][j]"):
            with self.assertRaises(ValueError):
                flatten_matrices(expression, SPECS["s114"])
        original = self.funcs["s114"][2]
        with self.assertRaisesRegex(ValueError, "mixed LEN/LEN2"):
            extract_computation(original.replace("i < LEN2;", "i < LEN;"), SPECS["s114"])

    def test_driver_allocates_matrix_and_packed_buffers_separately(self):
        code = driver([self.cases["s125"]], [1], 8, 1, matrix_sizes=[0, 3], stride_paddings=[0, 5])
        self.assertIn("got_aa = make_input(n * ld", code)
        self.assertIn("got_array = make_input(n * n", code)
        self.assertIn("fill_padding(got_aa, n, ld);", code)
        self.assertIn('check_padding("s125", "aa"', code)
        self.assertNotIn("fill_padding(got_array", code)

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_wrong_matrix_stride_is_rejected(self):
        candidates = self.root / "bad-stride"
        candidates.mkdir()
        original = (self.output / "kernels/s2102.c").read_text()
        candidates.joinpath("s2102.c").write_text(original.replace("* ld +", "* n +"))
        report = run_checks(self.output, names=["s2102"], candidate_dir=candidates,
                            matrix_sizes=[3], stride_paddings=[1], trials=1, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("row padding", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_matrix_transpose_mistake_is_rejected(self):
        candidates = self.root / "bad-transpose"
        candidates.mkdir()
        original = (self.output / "kernels/s1115.c").read_text()
        candidates.joinpath("s1115.c").write_text(original.replace(
            "cc[(size_t)(j) * ld + (i)]", "cc[(size_t)(i) * ld + (j)]"))
        report = run_checks(self.output, names=["s1115"], candidate_dir=candidates,
                            matrix_sizes=[3], stride_paddings=[0, 5], trials=8, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("s1115: aa[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_partial_matrix_writes_are_observable(self):
        candidates = self.root / "bad-triangle"
        candidates.mkdir()
        original = (self.output / "kernels/s114.c").read_text()
        candidates.joinpath("s114.c").write_text(original.replace("j < i;", "j < n;"))
        report = run_checks(self.output, names=["s114"], candidate_dir=candidates,
                            matrix_sizes=[3], stride_paddings=[0, 1], trials=2, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("s114: aa[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_hand_computed_matrix_results_without_source_reference(self):
        source = self.root / "matrix-values.c"
        source.write_text(r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int aa[6] = {1, 2, 777, 3, 4, 888};
    int bb[6] = {10, 20, 777, 30, 40, 888};
    int cc[6] = {2, 2, 777, 2, 2, 888};
    int packed[6] = {91, 92, 93, 94, 95, 96};
    s125(aa, packed, bb, cc, 2, 3);
    assert(packed[0] == 21 && packed[1] == 42);
    assert(packed[2] == 63 && packed[3] == 84);
    assert(packed[4] == 95 && packed[5] == 96);
    int identity[15];
    for (int i = 0; i < 15; ++i) identity[i] = 100 + i;
    s2102(identity, 3, 5);
    for (int row = 0; row < 3; ++row)
        for (int col = 0; col < 5; ++col)
            assert(identity[row*5+col] == (col < 3 ? row == col : 100+row*5+col));
    return 0;
}
''')
        binary = self.root / "matrix-values"
        command = ["clang", "-std=c11", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                   "-I", str(self.output), str(source), str(self.output / "kernels/s125.c"),
                   str(self.output / "kernels/s2102.c"), "-o", str(binary)]
        subprocess.run(command, check=True, capture_output=True, timeout=30)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=10)

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_schema_one_dataset_still_runs(self):
        legacy = self.root / "legacy-dataset"
        case = json.loads(json.dumps(self.cases["s124"]))
        for array in case["contract"]["arrays"]:
            array.pop("layout")
        for kind in ("kernel", "reference"):
            destination = legacy / case[kind]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.output / case[kind], destination)
        (legacy / "manifest.json").write_text(json.dumps({
            "schema_version": 1, "source_sha256": REVIEWED_SOURCE_SHA256, "cases": [case]}))
        report = run_checks(legacy, sizes=[0, 1, 9], trials=8, sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))
        self.assertEqual(report["matrix_cases"], [])

    def test_all_indirect_addressing_cases_are_supported(self):
        names = {name for name, case in self.cases.items() if case["category"] == "INDIRECT_ADDRESSING"}
        self.assertEqual(names, {"s491", "s4112", "s4113", "s4114", "s4115", "s4116", "s4117"})
        for name in names:
            self.assertEqual(self.cases[name]["status"], "generated")
        for name in ("s491", "s4112", "s4113", "s4114", "s4115", "s4116", "s353", "vag", "vas"):
            ip = next(a for a in self.cases[name]["contract"]["arrays"] if a["name"] == "ip")
            self.assertEqual(ip["access"], "read")
            self.assertEqual(ip["index_domain"]["minimum"], 0)
            self.assertEqual(ip["index_domain"]["maximum_exclusive"], "n")
            self.assertTrue(ip["index_domain"]["duplicates_allowed"])
            self.assertIn("const int *ip", self.cases[name]["signature"])

    def test_indirect_scalar_and_offset_contracts(self):
        c = self.cases["s4116"]["contract"]
        inputs = {s["name"]: s for s in c["scalar_inputs"]}
        self.assertEqual(inputs["j"]["domain"]["maximum"], "max(1,n)")
        self.assertEqual(inputs["inc"]["domain"]["maximum"], "INT_MAX-n")
        a = next(a for a in c["arrays"] if a["name"] == "a")
        self.assertEqual(a["minimum_elements"], "max(1, n+inc)")
        self.assertEqual(a["layout"], "offset_vector")
        n1 = self.cases["s4114"]["contract"]["scalar_inputs"][0]
        self.assertEqual(n1["domain"], {"id": "start_1based", "minimum": "1", "maximum": "n+1"})

    def test_indirect_reduction_observes_temp_instead_of_dummy_zero(self):
        for name in ("s4115", "s4116"):
            ref = (self.output / f"reference/{name}.c").read_text()
            kernel = (self.output / f"kernels/{name}.c").read_text()
            self.assertIn("dummy(a, b, c, d, e, aa, bb, cc, 0.);", ref)
            self.assertIn("temp = sum;", ref)
            self.assertIn("return temp;", ref)
            self.assertIn("return sum;", kernel)
            self.assertEqual(self.cases[name]["contract"]["scalar_output"]["observation"], "temp")
        damaged = self.funcs["s4115"][2].replace("temp = sum;", "temp = sum + 1;")
        with self.assertRaisesRegex(ValueError, "unreviewed post-loop"):
            extract_computation(damaged, SPECS["s4115"])

    def test_only_reviewed_nested_index_loads_are_lowered(self):
        source = "aa[j-1][ip[i]]"
        self.assertEqual(flatten_matrices(source, SPECS["s4116"]), "aa[(size_t)(j-1) * ld + (ip[i])]")
        for bad in ("aa[j-1][other[i]]", "aa[j-1][ip[i++]]", "aa[j-1][ip[ip[i]]]", "aa[j-1][ip[i]"):
            with self.assertRaises(ValueError):
                flatten_matrices(bad, SPECS["s4116"])
        ref = (self.output / "reference/s4116.c").read_text()
        self.assertIn("aa[j-1][ip[i]]", ref)
        self.assertIn("original_s4116((int *)arg_ip, arg_j, arg_inc, arg_ld)", ref)

    def test_nonstandard_scaffold_and_original_parameters_are_checked(self):
        body = extract_computation(self.funcs["s353"][2], SPECS["s353"])
        self.assertIn("int alpha = c[0];", body)
        self.assertIn("i += 5", body)
        self.assertIn("b[ip[i + 4]]", body)
        self.assertNotIn("clock", body)
        with self.assertRaisesRegex(ValueError, "start-clock"):
            extract_computation(self.funcs["s353"][2], KernelSpec(read="b c ip", update="a", pointer_params=("ip",), index_arrays="ip"))
        wrong = self.funcs["s491"][2].replace("int* __restrict__ ip", "int ip")
        with self.assertRaisesRegex(ValueError, "parameter interface mismatch"):
            extract_computation(wrong, SPECS["s491"])

    def test_size_contract_filter_does_not_round_up_or_invent_empty_reductions(self):
        self.assertEqual(eligible_sizes(self.cases["s353"], [0, 1, 5, 9, 10], []), [0, 5, 10])
        self.assertEqual(eligible_sizes(self.cases["s314"], [0, 1, 9], []), [1, 9])
        self.assertEqual(eligible_sizes(self.cases["s316"], [0], []), [])
        self.assertEqual(self.cases["s314"]["contract"]["empty_input"], "Not admitted by the size contract.")
        with self.assertRaises(ValueError):
            KernelSpec(write="ip", index_arrays="ip")
        with self.assertRaises(ValueError):
            KernelSpec(read="a", offset_vectors=(("a", "missing"),))

    def test_driver_initializes_and_compares_index_buffers(self):
        code = driver([self.cases["s4116"]], [1], 8, 1, matrix_sizes=[0, 3])
        self.assertIn("index_pattern < 6", code)
        self.assertLess(code.index("int scalar_inc ="), code.index("Buffer got_a ="))
        self.assertIn("got_a = make_input(n + scalar_inc", code)
        self.assertIn("fill_indices(got_ip, n, index_pattern);", code)
        self.assertLess(code.index("fill_indices(got_ip"), code.index("Buffer want_ip"))
        self.assertIn('compare("s4116", "ip"', code)

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_reordering_duplicate_scatter_stores_is_rejected(self):
        candidates = self.root / "bad-scatter-order"
        candidates.mkdir()
        source = (self.output / "kernels/vas.c").read_text()
        candidates.joinpath("vas.c").write_text(source.replace(
            "for (int i = 0; i < n; i++)", "for (int i = n-1; i >= 0; --i)"))
        report = run_checks(self.output, names=["vas"], sizes=[4], trials=4,
                            candidate_dir=candidates, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("vas: a[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_prefix_sum_array_is_checked_even_with_correct_scalar_result(self):
        candidates = self.root / "bad-prefix-output"
        candidates.mkdir()
        source = (self.output / "kernels/s3112.c").read_text()
        candidates.joinpath("s3112.c").write_text(source.replace("b[i] = sum;", "b[i] = 0;"))
        report = run_checks(self.output, names=["s3112"], sizes=[0, 5], trials=4,
                            candidate_dir=candidates, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("s3112: b[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_index_inputs_cannot_be_silently_modified(self):
        candidates = self.root / "bad-index-write"
        candidates.mkdir()
        source = (self.output / "kernels/vag.c").read_text()
        # Read ip normally, then illegally modify it after all gather loads.
        end = source.rfind("}")
        candidates.joinpath("vag.c").write_text(source[:end] + "((int *)ip)[0] = n;\n" + source[end:])
        report = run_checks(self.output, names=["vag"], sizes=[4], trials=1,
                            candidate_dir=candidates, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("vag: ip[", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_ignoring_sparse_dot_offset_is_rejected(self):
        candidates = self.root / "bad-offset"
        candidates.mkdir()
        source = (self.output / "kernels/s4116.c").read_text()
        candidates.joinpath("s4116.c").write_text(source.replace("off = inc + i;", "off = i;"))
        report = run_checks(self.output, names=["s4116"], matrix_sizes=[3], stride_paddings=[1],
                            trials=8, candidate_dir=candidates, sanitize=True)
        self.assertEqual(report["status"], "failed")
        self.assertIn("s4116: scalar", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_hand_computed_indirect_and_scalar_results(self):
        source = self.root / "indirect-values.c"
        source.write_text(r'''
#include <assert.h>
#include <limits.h>
#include "kernels.h"
int main(void) {
    int ip[4] = {2, 2, 0, 2};
    int b[4] = {1, 2, 3, 4};
    int c[4] = {10, 20, 30, 40};
    int a[4] = {100, 101, 102, 103};
    vas(a, b, ip, 4);
    assert(a[0] == 3 && a[1] == 101 && a[2] == 4 && a[3] == 103);
    s4113(a, b, c, ip, 4);
    assert(a[0] == 31 && a[1] == 101 && a[2] == 43 && a[3] == 103);
    int d[4] = {1, 1, 1, 1};
    int reverse_ip[4] = {0, 1, 1, 3};
    s4114(a, b, c, d, reverse_ip, 2, 4);
    assert(a[0] == 31 && a[1] == 32 && a[2] == 33 && a[3] == 14);
    s4114(a, b, c, d, reverse_ip, 5, 4);
    assert(a[0] == 31 && a[1] == 32 && a[2] == 33 && a[3] == 14);
    int values[4] = {2, 3, 5, 7}, factors[4] = {11, 13, 17, 19};
    assert(s4115(values, factors, ip, 4) == 259);
    assert(s4115(values, factors, ip, 0) == 0);
    int offset_a[5] = {100, 101, 2, 3, 104};
    int aa[15] = {1, 2, 3, 777, 888, 4, 5, 6, 777, 888, 7, 11, 13, 777, 888};
    int columns[3] = {2, 0, 1};
    assert(s4116(offset_a, aa, columns, 3, 2, 3, 5) == 47);
    assert(s4116(offset_a, aa, columns, 1, 0, 0, 1) == 0);
    int one_column[1] = {0};
    assert(s4116(offset_a, aa, one_column, 1, 0, 1, 1) == 0);
    int prefix[4] = {0};
    assert(s3112(values, prefix, 4) == 17);
    assert(prefix[0] == 2 && prefix[1] == 5 && prefix[2] == 10 && prefix[3] == 17);
    int signed_values[4] = {2, -3, 5, 7};
    assert(s314(signed_values, 4) == 7);
    assert(s316(signed_values, 4) == -3);
    int extremes[4] = {INT_MIN, 0, INT_MAX, -1};
    assert(s314(extremes, 4) == INT_MAX);
    assert(s316(extremes, 4) == INT_MIN);
    int unrolled_a[10] = {0}, unrolled_b[10], unrolled_c[10] = {2}, repeated[10];
    for (int i = 0; i < 10; ++i) { unrolled_b[i] = i+1; repeated[i] = 9; }
    s353(unrolled_a, unrolled_b, unrolled_c, repeated, 10);
    for (int i = 0; i < 10; ++i) assert(unrolled_a[i] == 20);
    s353(unrolled_a, unrolled_b, unrolled_c, repeated, 0);
    for (int i = 0; i < 10; ++i) assert(unrolled_a[i] == 20);
    return 0;
}
''')
        binary = self.root / "indirect-values"
        names = ["vas", "s4113", "s4114", "s4115", "s4116", "s3112", "s314", "s316", "s353"]
        command = ["clang", "-std=c11", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                   "-I", str(self.output), str(source),
                   *(str(self.output / f"kernels/{name}.c") for name in names), "-o", str(binary)]
        subprocess.run(command, check=True, capture_output=True, timeout=30)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=10)

    @unittest.skipUnless(shutil.which("clang"), "integration tests require clang")
    def test_schema_two_matrix_dataset_still_runs(self):
        legacy = self.root / "legacy-matrix"
        case = self.cases["s114"]
        for kind in ("kernel", "reference"):
            destination = legacy / case[kind]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.output / case[kind], destination)
        (legacy / "manifest.json").write_text(json.dumps({
            "schema_version": 2, "source_sha256": REVIEWED_SOURCE_SHA256, "cases": [case]}))
        report = run_checks(legacy, matrix_sizes=[0, 1, 3], trials=8, sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))
        self.assertEqual(report["indexed_cases"], [])


if __name__ == "__main__":
    unittest.main()
