"""Helpers, explicit scalar state, packing, and overflow-safe input profiles."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_tsvc_kernels import DRIVER_SUPPORT, driver, run_checks
from extract_tsvc_int import DEFAULT_SOURCE, functions
from generate_tsvc_kernels import digest, extract_computation, generate, helper_sources
from tsvc_kernel_specs import HELPERS, SPECS, KernelSpec


@unittest.skipUnless(DEFAULT_SOURCE.exists(), "requires the reviewed llvm-test-suite checkout")
class ExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="tsvc-extension-unit-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.output = cls.root / "dataset"
        cls.manifest = generate(DEFAULT_SOURCE, cls.output)
        cls.cases = {case["name"]: case for case in cls.manifest["cases"]}
        cls.source = DEFAULT_SOURCE.read_text()
        cls.functions = functions(cls.source)

    def test_helpers_are_local_parameterized_and_have_provenance(self):
        sources = helper_sources(self.source)
        for name in ("s151", "s152", "s31111", "s4121"):
            kernel = (self.output / f"kernels/{name}.c").read_text()
            ref = (self.output / f"reference/{name}.c").read_text()
            for helper in SPECS[name].helpers:
                self.assertIn(f"static int tsvc_{helper}(", kernel)
                self.assertIn(f"static int {helper}(", ref)
                self.assertIn({"name": helper, "source_sha256": digest(sources[helper])}, self.cases[name]["helpers"])
            self.assertNotIn("[LEN]", ref)
        self.assertIn("tsvc_s151s(a, b, 1, n)", (self.output / "kernels/s151.c").read_text())
        self.assertIn("i < LEN-1", (self.output / "reference/s151.c").read_text())
        self.assertEqual(set(sources), set(HELPERS))

    def test_unknown_helpers_and_transitive_calls_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unreviewed helper interface"):
            helper_sources(self.source.replace("TYPE test(TYPE* A)", "TYPE test(TYPE* A, int extra)"))
        with self.assertRaisesRegex(ValueError, "transitive calls"):
            helper_sources(self.source.replace("s += A[i];", "s += unknown(A[i]);"))
        with self.assertRaisesRegex(ValueError, "unreviewed computation calls"):
            extract_computation(self.functions["s151"][2], KernelSpec(read="b", update="a"))
        with self.assertRaisesRegex(ValueError, "array interface mismatch"):
            extract_computation(self.functions["s151"][2].replace("s151s(a, b,  1)", "s151s(a, c,  1)"), SPECS["s151"])
        with self.assertRaises(ValueError):
            KernelSpec(helpers=("unknown",))

    def test_fixed_trip_helper_is_not_generalized_to_n(self):
        kernel = (self.output / "kernels/s31111.c").read_text()
        self.assertIn("(void)n;", kernel)
        self.assertEqual(kernel.count("sum += tsvc_test("), 8)
        self.assertIn("i < 4", kernel)
        self.assertIn("&a[28]", kernel)
        self.assertEqual(self.cases["s31111"]["contract"]["size"]["minimum"], 32)
        with self.assertRaisesRegex(ValueError, "no requested sizes"):
            run_checks(self.output, names=["s31111"], sizes=[0, 1, 31])

    def test_scalar_slots_and_distinct_observations_are_explicit(self):
        case = self.cases["s3110"]
        self.assertEqual([o["source_variable"] for o in case["contract"]["scalar_outputs"]],
                         ["max", "xindex", "yindex", "chksum"])
        self.assertEqual(case["contract"]["scalar_output"]["source_expression"], "max + xindex+1 + yindex+1")
        self.assertEqual(case["contract"]["dummy_observation"], "chksum")
        self.assertIn("pairwise disjoint", case["contract"]["aliasing"])
        ref = (self.output / "reference/s3110.c").read_text()
        self.assertIn("reference_output_xindex = (xindex)", ref)
        self.assertIn("temp = max + xindex+1 + yindex+1;", ref)
        self.assertIn("*arg_out_xindex = reference_output_xindex;", ref)
        bad = self.functions["s3110"][2].replace("temp = max + xindex+1 + yindex+1;", "temp = max;")
        with self.assertRaisesRegex(ValueError, "unreviewed post-loop"):
            extract_computation(bad, SPECS["s3110"])
        with self.assertRaisesRegex(ValueError, "must be exposed"):
            KernelSpec(result="value", dummy_result="chksum")

    def test_missing_scalar_observation_cannot_be_dropped(self):
        with self.assertRaisesRegex(ValueError, "unexposed dummy observation"):
            extract_computation(self.functions["s311"][2], KernelSpec(read="a"))

    def test_integer_abs_has_a_domain_and_an_independent_reference_primitive(self):
        self.assertEqual(self.cases["s3113"]["contract"]["arrays"][0]["value_domain"]["minimum"], -2147483647)
        self.assertIn("tsvc_abs(a[i])", (self.output / "kernels/s3113.c").read_text())
        ref = (self.output / "reference/s3113.c").read_text()
        self.assertIn("#define FABS(value) abs(value)", ref)
        self.assertIn("FABS(a[i])", ref)
        with self.assertRaises(ValueError):
            KernelSpec(integer_abs=True)

    def test_profiles_are_test_recipes_not_caller_restrictions(self):
        for name in ("s312", "s321", "s322"):
            self.assertFalse(self.cases[name]["testing"]["contract_restriction"])
            self.assertNotIn("value_domain", self.cases[name]["contract"]["arrays"][0])
        self.assertIn("returns 1", self.cases["s312"]["contract"]["empty_input"])
        self.assertIn("out_index=-2", self.cases["s332"]["contract"]["empty_input"])
        code = driver([self.cases["s322"], self.cases["s3110"]], [8, 9], 8, 1)
        self.assertLess(code.index("prepare_recurrence(got_b, &got_c"), code.index("Buffer want_a"))
        self.assertIn("got_out_max = make_input(1, trial, guard)", code)
        self.assertIn('compare("s3110", "out_chksum"', code)

    def compile_and_run(self, stem, source, kernels=()):
        cfile, binary = self.root / f"{stem}.c", self.root / stem
        cfile.write_text(source)
        command = ["clang", "-std=c11", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                   "-I", str(self.output), str(cfile),
                   *(str(self.output / f"kernels/{name}.c") for name in kernels), "-o", str(binary)]
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        executed = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
        self.assertEqual(executed.returncode, 0, executed.stderr)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_helpers_products_and_recurrences(self):
        self.compile_and_run("helper-values", r'''
#include <assert.h>
#include <limits.h>
#include "kernels.h"
int main(void) {
    int a[4] = {1,2,3,4}, b[4] = {10,20,30,40};
    s151(a,b,4);
    assert(a[0]==12 && a[1]==23 && a[2]==34 && a[3]==4);
    s151(a,b,0); /* helper pointer parameters must not evaluate a zero VLA bound */
    assert(a[0]==12 && a[3]==4);
    int x[2]={1,2}, y[2]={9,9}, c[2]={3,-2}, d[2]={2,4}, e[2]={5,-3};
    s152(x,y,c,d,e,2);
    assert(x[0]==31 && x[1]==26 && y[0]==10 && y[1]==-12);
    s4121(x,y,c,2);
    assert(x[0]==61 && x[1]==50);
    int prefix[37];
    for(int i=0;i<37;++i) prefix[i]=i<32 ? i+1 : INT_MAX;
    assert(s31111(prefix,37)==528);
    int factors[3]={2,-3,4}, extremes[1]={INT_MIN};
    assert(s312(factors,3)==-24 && s312(factors,0)==1);
    assert(s312(extremes,1)==INT_MIN);
    int absolute[3]={-INT_MAX,0,7};
    assert(s3113(absolute,3)==INT_MAX);
    int rec1[4]={1,1,1,1}, coeff1[4]={0,2,-1,3};
    s321(rec1,coeff1,4);
    assert(rec1[0]==1 && rec1[1]==3 && rec1[2]==-2 && rec1[3]==-5);
    int rec2[4]={1,2,3,4}, coeff2[4]={1,1,2,-1}, coeff3[4]={1,1,-1,2};
    s322(rec2,coeff2,coeff3,4);
    assert(rec2[0]==1 && rec2[1]==2 && rec2[2]==6 && rec2[3]==2);
    int early[4]={10,20,30,40}, eb[4]={1,1,1,1}, ec[4]={0,2,3,4};
    s482(early,eb,ec,4);
    assert(early[0]==10 && early[1]==22 && early[2]==30 && early[3]==40);
    return 0;
}
''', ["s151", "s152", "s4121", "s31111", "s312", "s3113", "s321", "s322", "s482"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_scalar_state_and_packing(self):
        self.compile_and_run("scalar-values", r'''
#include <assert.h>
#include <limits.h>
#include "kernels.h"
int main(void) {
    int aa[6]={1,7,999,7,2,888};
    int maximum=0, row=0, col=0, checksum=0;
    assert(s3110(aa,&maximum,&row,&col,&checksum,2,3)==10);
    assert(maximum==7 && row==0 && col==1 && checksum==8);
    assert(s13110(aa,&maximum,&row,&col,&checksum,2,3)==9);
    assert(maximum==7 && row==0 && col==0 && checksum==7);
    int near_limit[1]={INT_MAX-2};
    assert(s3110(near_limit,&maximum,&row,&col,&checksum,1,1)==INT_MAX);
    int values[4]={-3,4,-1,0}, index=0;
    assert(s331(values,&index,&checksum,4)==3 && index==2 && checksum==2);
    assert(s331(values,&index,&checksum,0)==0 && index==-1 && checksum==-1);
    int search[4]={4,4,5,6};
    assert(s332(search,&index,&checksum,4,4)==5 && index==2 && checksum==7);
    assert(s332(search,&index,&checksum,6,4)==-1 && index==-2 && checksum==-3);
    assert(s332(search,&index,&checksum,0,0)==-1 && index==-2 && checksum==-3);
    int out[4]={90,91,92,93}, packed_input[4]={-2,7,0,9};
    s341(out,packed_input,4);
    assert(out[0]==7 && out[1]==9 && out[2]==92 && out[3]==93);
    int mask[4]={1,-1,2,0}, sequence[4]={11,22,33,44};
    s342(mask,sequence,4);
    assert(mask[0]==11 && mask[1]==-1 && mask[2]==22 && mask[3]==0);
    int matrix[6]={11,12,777,21,22,888}, select[6]={1,1,777,1,0,888};
    int flat[4]={90,91,92,93};
    s343(matrix,flat,select,2,3);
    assert(flat[0]==11 && flat[1]==21 && flat[2]==12 && flat[3]==93);
    assert(matrix[2]==777 && matrix[5]==888 && select[2]==777 && select[5]==888);
    return 0;
}
''', ["s3110", "s13110", "s331", "s332", "s341", "s342", "s343"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_profile_construction_bounds_and_nonzero_large_products(self):
        self.compile_and_run("profile-values", DRIVER_SUPPORT + r'''
#include <assert.h>
int main(void) {
    rng_state=42;
    for(int trial=0;trial<24;++trial) {
        Buffer a=make_input(4096,trial,16), b=make_input(4096,trial,16), c=make_input(4096,trial,16);
        prepare_product(a,4096,trial);
        int64_t product=1;
        for(int i=0;i<4096;++i) {
            product*=a.data[i];
            assert(product>=-387420489 && product<=387420489);
        }
        if(trial==5) assert(product==387420489);
        prepare_recurrence(b,&c,4096,trial);
        for(int i=0;i<4096;++i) {
            assert(b.data[i]>=-1 && b.data[i]<=1 && c.data[i]>=-1 && c.data[i]<=1);
            assert(b.data[i]==0 || c.data[i]==0);
        }
        free(a.base); free(b.base); free(c.base);
    }
    return 0;
}
''')

    def bad_candidate(self, name, before, after, **options):
        candidates = Path(tempfile.mkdtemp(prefix=f"bad-{name}-", dir=self.root))
        source = (self.output / f"kernels/{name}.c").read_text()
        self.assertIn(before, source)
        (candidates / f"{name}.c").write_text(source.replace(before, after))
        report = run_checks(self.output, names=[name], candidate_dir=candidates, sanitize=True, **options)
        self.assertEqual(report["status"], "failed")
        return report["error"]

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_wrong_scalar_slot_fails_even_when_return_value_matches(self):
        error = self.bad_candidate("s3110", "*out_xindex = xindex;", "*out_xindex = xindex+1;",
                                   matrix_sizes=[2], trials=1)
        self.assertIn("s3110: out_xindex[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_extrema_tie_order_is_checked(self):
        error = self.bad_candidate("s3110", "] > max)", "] >= max)", matrix_sizes=[2], trials=2)
        self.assertIn("s3110: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_packing_order_and_untouched_suffix_are_checked(self):
        error = self.bad_candidate("s343", "aa[(size_t)(j) * ld + (i)]", "aa[(size_t)(i) * ld + (j)]",
                                   matrix_sizes=[3], trials=8)
        self.assertIn("s343: array[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_dropping_a_helper_call_is_rejected(self):
        error = self.bad_candidate("s152", "tsvc_s152s(a, b, c, i);", ";", sizes=[3], trials=2)
        self.assertIn("s152: a[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_empty_product_identity_is_checked(self):
        error = self.bad_candidate("s312", "prod = (int)1;", "prod = (int)0;", sizes=[0], trials=1)
        self.assertIn("s312: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_schema_three_indexed_dataset_still_runs(self):
        legacy = self.root / "legacy-three"
        case = json.loads(json.dumps(self.cases["s4116"]))
        case.pop("testing")
        case.pop("helpers")
        case["contract"].pop("scalar_outputs")
        for kind in ("kernel", "reference"):
            target = legacy / case[kind]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.output / case[kind], target)
        (legacy / "manifest.json").write_text(json.dumps({
            "schema_version": 3, "source_sha256": self.manifest["source_sha256"], "cases": [case]}))
        report = run_checks(legacy, matrix_sizes=[0,1,3], trials=8, sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))
        self.assertEqual(report["indexed_cases"], ["s4116"])


if __name__ == "__main__":
    unittest.main()
