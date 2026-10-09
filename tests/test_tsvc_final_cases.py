"""Final TSVC cases: explicit semantic adaptations and difficult numeric domains."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_tsvc_kernels import DRIVER_SUPPORT, driver, eligible_sizes, run_checks
from extract_tsvc_int import DEFAULT_SOURCE, functions
from generate_tsvc_kernels import extract_computation, generate
from tsvc_kernel_specs import SPECS, KernelSpec


@unittest.skipUnless(DEFAULT_SOURCE.exists(), "requires the reviewed llvm-test-suite checkout")
class FinalCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="tsvc-final-unit-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.output = cls.root / "dataset"
        cls.manifest = generate(DEFAULT_SOURCE, cls.output)
        cls.cases = {case["name"]: case for case in cls.manifest["cases"]}
        cls.funcs = functions(DEFAULT_SOURCE.read_text())

    def test_all_cases_and_semantic_caveats_are_explicit(self):
        self.assertEqual(len(self.cases), 151)
        self.assertTrue(all(c["status"] == "generated" for c in self.cases.values()))
        fractional = {"s254", "s255", "s291", "s292", "s317"}
        caveats = {name for name, case in self.cases.items() if case.get("experiment_caveats")}
        self.assertEqual(caveats, fractional | {"s451", "s481", "s258", "vbor"})
        for name in fractional:
            c = self.cases[name]["contract"]
            self.assertEqual(c["numeric_adaptation"]["kind"], "degenerate_fractional_cast")
            self.assertEqual(c["numeric_adaptation"]["casts"][0]["integer_value"], 0)
            self.assertIn("(int)0", (self.output / f"kernels/{name}.c").read_text())
            self.assertIn("(TYPE).", (self.output / f"reference/{name}.c").read_text())
        self.assertEqual(self.cases["s317"]["signature"], "int s317(int n)")
        self.assertFalse(self.cases["s451"]["contract"]["numeric_adaptation"]["pure_integer"])
        self.assertFalse(self.cases["s481"]["contract"]["termination"]["process_termination"])

    def test_new_rewrite_sites_are_exact_not_a_general_relaxation(self):
        changes = [
            ("s254", "(TYPE).5", "(TYPE).25"),
            ("s315", "(i * 7)", "(i * 8)"),
            ("s451", "cos(c[i])", "cos(b[i])"),
            ("s481", "d[i] <", "d[i] <="),
            ("s481", "exit (0)", "exit (1)"),
            ("s2111", "temp = 3.;", "temp = 4.;"),
            ("s258", "aa[0][i]", "aa[1][i]"),
            ("s258", "s = 0.;", "s = LEN2;"),
        ]
        for name, old, new in changes:
            with self.subTest(name=name, change=old), self.assertRaises(ValueError):
                extract_computation(self.funcs[name][2].replace(old, new), SPECS[name])
        with self.assertRaises(ValueError):
            extract_computation(self.funcs["s254"][2], KernelSpec(read="b", write="a"))
        with self.assertRaises(ValueError):
            KernelSpec(fractional_casts=(".75",))
        with self.assertRaises(ValueError):
            KernelSpec(single_row_matrix=True)
        with self.assertRaises(ValueError):
            KernelSpec(termination=True)

    def test_size_holes_initialization_and_stride_observations(self):
        self.assertEqual(eligible_sizes(self.cases["s292"], [0,1,2,3], []), [0,2,3])
        with self.assertRaisesRegex(ValueError, "no requested sizes"):
            run_checks(self.output, names=["s292"], sizes=[1])
        for name, minimum in (("s254",1), ("s255",2), ("s315",1), ("s318",1)):
            self.assertEqual(self.cases[name]["contract"]["size"]["minimum"], minimum)
        for kind in ("kernels", "reference"):
            self.assertNotIn("(i * 7)", (self.output / f"{kind}/s315.c").read_text())
        c = self.cases["s315"]["contract"]
        self.assertIn("(i * 7)", c["removed_benchmark_initializers"][0])
        self.assertEqual(c["scalar_output"]["source_expression"], "index+x+1")
        self.assertEqual([o["source_variable"] for o in c["scalar_outputs"]], ["x","index","chksum"])
        c = self.cases["s318"]["contract"]
        self.assertEqual(c["arrays"][0]["minimum_elements"], "max(1, n*inc)")
        self.assertEqual(c["arrays"][0]["value_domain"]["minimum"], -2147483647)
        code = driver([self.cases["s292"], self.cases["s318"]], [0,1,2], 12, 1)
        self.assertIn("sizes[i] != 1", code)
        self.assertIn("make_input(n * scalar_inc", code)

    def test_single_row_allocations_and_reference_indexing(self):
        for name in ("s258", "vbor"):
            case = self.cases[name]
            aa = next(a for a in case["contract"]["arrays"] if a["name"] == "aa")
            self.assertEqual(aa["minimum_elements"], "max(1, ld)")
            self.assertEqual(aa["logical_rows"], 1)
            self.assertEqual(case["contract"]["row_stride"]["logical_shape"], "1 by n (single row)")
            self.assertIn("aa[0][i]", (self.output / f"reference/{name}.c").read_text())
            code = driver([case], [0], 12, 1, matrix_sizes=[0,1,3])
            self.assertIn("got_aa = make_input(ld,", code)
            self.assertIn("fill_row_padding(got_aa", code)
            self.assertIn(f'check_row_padding("{name}", "aa"', code)

    def test_profiles_do_not_narrow_caller_contracts(self):
        for name in ("s115", "s118", "s232", "s2111", "vbor"):
            case = self.cases[name]
            self.assertFalse(case["testing"]["contract_restriction"])
            self.assertTrue(all("value_domain" not in a for a in case["contract"]["arrays"]))
            code = driver([case], [0], 12, 1)
            self.assertLess(code.index("    prepare_"), code.index("    Buffer want_"))
        ref = (self.output / "reference/s481.c").read_text()
        self.assertIn("exit (0);", ref)
        self.assertIn("reference_stop_index = i; return 0;", ref)
        self.assertIn("reference_stop_index = -1;", ref)
        self.assertIn("#undef USE_FLOAT_TRIG", (self.output / "reference/s451.c").read_text())
        code = driver([self.cases["s481"]], [0,1,3], 12, 1)
        self.assertIn("index_pattern < 4", code)
        self.assertIn("prepare_termination(got_d, n, index_pattern)", code)

    def compile_and_run(self, stem, source, names=(), flags=()):
        cfile, binary = self.root / f"{stem}.c", self.root / stem
        cfile.write_text(source)
        command = ["clang", "-std=c11", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                   *flags, "-I", str(self.output), str(cfile),
                   *(str(self.output / f"kernels/{name}.c") for name in names), "-lm", "-o", str(binary)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_matrices_and_checksum_fallback(self):
        self.compile_and_run("matrix-values", r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int aa[15]={0}; aa[1]=2; aa[2]=-1; aa[7]=3;
    int a[3]={2,3,4}, other[3]={2,3,4};
    s115(a,aa,3,5); assert(a[0]==2 && a[1]==-1 && a[2]==9);
    s118(other,aa,3,5); assert(other[0]==2 && other[1]==7 && other[2]==3);
    int squares[12]={11,12,13,99, 2,5,6,99, 3,7,8,99};
    int bb[12]={0}; bb[5]=-1; bb[9]=-2; bb[10]=-3;
    s232(squares,bb,3,4);
    assert(squares[5]==3 && squares[9]==7 && squares[10]==46);
    assert(squares[0]==11 && squares[6]==6 && squares[7]==99 && squares[11]==99);
    int wave[12]={1,2,3,99, 4,-8,-8,99, 5,-8,-8,99};
    assert(s2111(wave,3,4)==61);
    assert(wave[5]==6 && wave[6]==9 && wave[9]==11 && wave[10]==20 && wave[11]==99);
    int single[2]={-2,99}; assert(s2111(single,1,2)==-2 && single[1]==99);
    single[0]=0; assert(s2111(single,1,2)==3 && single[0]==0);
    single[0]=71; assert(s2111(single,0,2)==3 && single[0]==71);
    return 0;
}
''', ["s115", "s118", "s232", "s2111"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_extrema_and_logical_stride_index(self):
        self.compile_and_run("max-values", r'''
#include <assert.h>
#include <limits.h>
#include "kernels.h"
int main(void) {
    int a[5]={-4,9,9,-2,7}, value=-1, index=-1, sum=-1;
    assert(s315(a,&value,&index,&sum,5)==11);
    assert(value==9 && index==1 && sum==10 && a[0]==-4 && a[4]==7);
    int strided[6]={-5,111,9,222,-9,333};
    assert(s318(strided,&value,&index,&sum,2,3)==11);
    assert(value==9 && index==1 && sum==10 && strided[5]==333);
    int same[1]={-7};
    assert(s318(same,&value,&index,&sum,0,4)==8);
    assert(value==7 && index==0 && sum==7);
    int large[1]={-INT_MAX+1};
    assert(s318(large,&value,&index,&sum,0,1)==INT_MAX && value==INT_MAX-1);
    return 0;
}
''', ["s315", "s318"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_fractional_casts_and_empty_cases(self):
        self.compile_and_run("fraction-values", r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int b[3]={2,-5,8}, a[3]={17,18,19};
    s254(a,b,3); for(int i=0;i<3;++i) assert(a[i]==0);
    a[0]=19; s255(a,b,3); assert(a[0]==0);
    a[0]=19; s291(a,b,0); assert(a[0]==19);
    s291(a,b,3); assert(a[0]==0 && a[2]==0);
    a[0]=19; s292(a,b,0); assert(a[0]==19);
    s292(a,b,2); assert(a[0]==0 && a[1]==0);
    assert(b[0]==2 && b[1]==-5 && b[2]==8);
    assert(s317(0)==1 && s317(1)==1 && s317(2)==0 && s317(3)==0 && s317(32)==0);
    return 0;
}
''', ["s254", "s255", "s291", "s292", "s317"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_single_row_and_nontrivial_products(self):
        self.compile_and_run("row-values", r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int a[4]={1,-1,0,2}, c[4]={2,3,4,5}, d[4]={3,4,-2,1};
    int aa[6]={2,3,5,7,123,456}, b[4]={0}, e[4]={0};
    s258(a,aa,b,c,d,e,4,6);
    assert(b[0]==21 && b[1]==31 && b[2]==34 && b[3]==6);
    assert(e[0]==20 && e[1]==30 && e[2]==50 && e[3]==14 && aa[5]==456);
    int pa[2]={2,2}, pb[2]={2,2}, pc[2]={2,2}, pd[2]={2,2}, pe[2]={2,2};
    int row[4]={2,2,123,456}, x[2]={-9,-9};
    assert(vbor(pa,row,pb,pc,pd,pe,x,2,4)==1474560);
    assert(x[0]==737280 && x[1]==737280 && row[2]==123 && row[3]==456);
    pa[0]=pb[0]=pc[0]=pd[0]=pe[0]=row[0]=3;
    assert(vbor(pa,row,pb,pc,pd,pe,x,1,4)==95659380 && x[1]==737280);
    assert(vbor(pa,row,pb,pc,pd,pe,x,0,4)==0 && x[0]==95659380);
    return 0;
}
''', ["s258", "vbor"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_trig_conversion_and_stop_before_update(self):
        self.compile_and_run("outcome-values", r'''
#include <assert.h>
#include <limits.h>
#include <math.h>
#include "kernels.h"
int main(void) {
    int b[8]={0,1,-1,2,-2,3,INT_MIN,INT_MAX}, c[8]={0,0,0,0,0,0,INT_MAX,INT_MIN}, a[8]={0};
    s451(a,b,c,8);
    int expected[6]={1,1,0,1,0,1};
    for(int i=0;i<6;++i) assert(a[i]==expected[i]);
    for(int i=6;i<8;++i) assert(a[i]==(int)(sin((double)b[i])+cos((double)c[i])));
    int ta[4]={10,20,30,40}, tb[4]={2,3,INT_MAX,4}, tc[4]={3,4,INT_MAX,5}, td[4]={0,0,-1,0};
    assert(s481(ta,tb,tc,td,4)==2);
    assert(ta[0]==16 && ta[1]==32 && ta[2]==30 && ta[3]==40);
    td[0]=INT_MIN;
    assert(s481(ta,tb,tc,td,4)==0 && ta[0]==16);
    td[0]=td[2]=0; tb[2]=1; tc[2]=2;
    assert(s481(ta,tb,tc,td,4)==-1 && ta[2]==32 && ta[3]==60);
    assert(s481(ta,tb,tc,td,0)==-1 && ta[3]==60);
    return 0;
}
''', ["s451", "s481"], ["-DUSE_FLOAT_TRIG"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_matrix_profile_bounds_and_padding(self):
        self.compile_and_run("profile-bounds", DRIVER_SUPPORT + r'''
#include <assert.h>
static int checked(int64_t value) { assert(value>=INT_MIN && value<=INT_MAX); return (int)value; }
int main(void) {
    rng_state=42;
    for(int n=1;n<=128;++n) for(int trial=0;trial<12;++trial) {
        int ld=n+3;
        Buffer coef=make_input(n*ld,trial,0), a=make_input(n,trial,0), other=copy_input(a,n,0);
        fill_padding(coef,n,ld);
        prepare_triangular(coef,n,ld,trial);
        for(int j=0;j<n;++j) for(int i=j+1;i<n;++i)
            a.data[i]=checked((int64_t)a.data[i]-checked((int64_t)coef.data[j*ld+i]*a.data[j]));
        for(int i=1;i<n;++i) for(int j=0;j<i;++j)
            other.data[i]=checked((int64_t)other.data[i]+checked((int64_t)coef.data[j*ld+i]*other.data[i-j-1]));
        if(n>8) for(int i=0;i<n;++i) { assert(abs(a.data[i])<=3*(i+1)); assert(abs(other.data[i])<=3*(i+1)); }
        free(a.base); free(other.base); free(coef.base);
        Buffer aa=make_input(n*ld,trial,0), bb=make_input(n*ld,trial,0);
        fill_padding(aa,n,ld); fill_padding(bb,n,ld);
        prepare_triangular_squares(aa,bb,n,ld);
        int changes=0;
        for(int j=1;j<n;++j) for(int i=1;i<=j;++i) {
            int value=checked(checked((int64_t)aa.data[j*ld+i-1]*aa.data[j*ld+i-1])+(int64_t)bb.data[j*ld+i]);
            changes += value != aa.data[j*ld+i]; aa.data[j*ld+i]=value;
            if(n>5) assert(abs(value)<=3);
        }
        if(n>5 && trial==1) assert(changes>0);
        for(int j=0;j<n;++j) for(int i=n;i<ld;++i) {
            assert(aa.data[j*ld+i]==sentinel(j*ld+i)); assert(bb.data[j*ld+i]==sentinel(j*ld+i));
        }
        free(aa.base); free(bb.base);
        aa=make_input(n*ld,trial,0); fill_padding(aa,n,ld);
        prepare_wavefront(aa,n,ld,trial);
        for(int j=1;j<n;++j) for(int i=1;i<n;++i)
            aa.data[j*ld+i]=checked((int64_t)aa.data[j*ld+i-1]+aa.data[(j-1)*ld+i]);
        int sum=0;
        for(int j=0;j<n;++j) for(int i=0;i<n;++i) {
            if(n>8) assert(abs(aa.data[j*ld+i])<=6);
            sum=checked((int64_t)sum+aa.data[j*ld+i]);
        }
        free(aa.base);
    }
    return 0;
}
''')

    def candidate(self, name, transform, **kwargs):
        directory = Path(tempfile.mkdtemp(prefix=f"bad-{name}-", dir=self.root))
        original = (self.output / f"kernels/{name}.c").read_text()
        changed = transform(original)
        self.assertNotEqual(changed, original)
        (directory / f"{name}.c").write_text(changed)
        report = run_checks(self.output, names=[name], candidate_dir=directory, sanitize=True, **kwargs)
        self.assertEqual(report["status"], "failed")
        return report["error"]

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_wrong_fractional_policy_and_product_identity_are_rejected(self):
        error = self.candidate("s254", lambda s: s.replace("(int)0;", "(int)1;"), sizes=[1,3], trials=2)
        self.assertIn("s254: a[", error)
        error = self.candidate("s317", lambda s: s.replace("return q;", "return 0;"), sizes=[0,1,2], trials=2)
        self.assertIn("s317: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_logical_index_and_maximum_ties_are_checked(self):
        error = self.candidate("s318", lambda s: s.replace("index = i;", "index = k;"), sizes=[9], trials=8)
        self.assertIn("s318:", error)
        error = self.candidate("s315", lambda s: s.replace("a[i] > x", "a[i] >= x"), sizes=[3], trials=2)
        self.assertIn("s315: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_wavefront_order_and_checksum_fallback_are_checked(self):
        error = self.candidate("s2111", lambda s: s.replace("j = 1; j < n; j++", "j = n-1; j >= 1; j--"),
                               matrix_sizes=[3,9], trials=8)
        self.assertIn("s2111:", error)
        error = self.candidate("s2111", lambda s: s.replace("if (checksum == 0) checksum = 3;", ""),
                               matrix_sizes=[0,1], trials=1)
        self.assertIn("s2111: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_trig_final_conversion_and_library_linkage(self):
        error = self.candidate("s451", lambda s: s.replace("sin(b[i]) + cos(c[i])", "(int)sin(b[i]) + (int)cos(c[i])"),
                               sizes=[3,9], trials=8)
        self.assertIn("s451: a[", error)
        report = run_checks(self.output, names=["s451"], sizes=[0,1,9], trials=8, sanitize=True, cc="clang -DUSE_FLOAT_TRIG")
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))
        self.assertTrue(any("-lm" in command for command in report["commands"]))
        report = run_checks(self.output, names=["s451"], sizes=[1], trials=1, cc="clang -ffast-math")
        self.assertEqual(report["status"], "failed")
        self.assertIn("requires strict math", report["error"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_stop_outcome_and_untouched_suffix_are_checked(self):
        error = self.candidate("s481", lambda s: s.replace("return i;", "return -1;"), sizes=[3], trials=4)
        self.assertIn("s481: scalar", error)
        error = self.candidate("s481", lambda s: s.replace("return i;", "a[i] += b[i]*c[i]; return i;"), sizes=[3], trials=4)
        self.assertIn("s481: a[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_single_row_padding_and_carry_are_checked(self):
        error = self.candidate("s258", lambda s: s.replace("if (a[i] > 0)", "s = 0; if (a[i] > 0)"),
                               matrix_sizes=[3], trials=4)
        self.assertIn("s258: b[", error)
        error = self.candidate("vbor", lambda s: s.replace("return checksum;", "((int*)aa)[n] = 7; return checksum;"),
                               matrix_sizes=[3], stride_paddings=[1], trials=2)
        self.assertIn("single-row padding", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_schema_five_alias_dataset_still_runs(self):
        directory = self.root / "schema-five"
        case = self.cases["s424"]
        for kind in ("kernel", "reference"):
            destination = directory / case[kind]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.output / case[kind], destination)
        (directory / "manifest.json").write_text(json.dumps({
            "schema_version": 5, "source_sha256": self.manifest["source_sha256"], "cases": [case]}))
        report = run_checks(directory, sizes=[0,1,65,66,129], trials=8, sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))


if __name__ == "__main__":
    unittest.main()
