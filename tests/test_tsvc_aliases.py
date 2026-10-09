"""Shared backing storage, symbolic strides, selectors, and retained postludes."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_tsvc_kernels import DEFAULT_SIZES, DRIVER_SUPPORT, SELECTOR_PATTERNS, driver, run_checks, scalar_test_value
from extract_tsvc_int import DEFAULT_SOURCE, functions
from generate_tsvc_kernels import extract_computation, generate, without_comments
from tsvc_kernel_specs import SPECS, KernelSpec, PointerView


@unittest.skipUnless(DEFAULT_SOURCE.exists(), "requires the reviewed llvm-test-suite checkout")
class AliasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="tsvc-alias-unit-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.output = cls.root / "dataset"
        cls.manifest = generate(DEFAULT_SOURCE, cls.output)
        cls.cases = {case["name"]: case for case in cls.manifest["cases"]}
        cls.funcs = functions(DEFAULT_SOURCE.read_text())

    def test_additional_categories_are_complete(self):
        for category in ("EQUIVALENCING", "SYMBOLICS", "NODE_SPLITTING", "INDUCTION_VARIABLE", "LOOP_REROLLING"):
            cases = [case for case in self.cases.values() if case["category"] == category]
            self.assertTrue(cases)
            self.assertTrue(all(case["status"] == "generated" for case in cases), category)
        self.assertTrue({10, 11, 66, 67}.issubset(DEFAULT_SIZES))

    def test_views_have_one_backing_buffer_not_disjoint_copies(self):
        for name in ("s421", "s1421", "s422", "s423", "s424"):
            c = self.cases[name]["contract"]
            names = {entry["name"] for entry in c["arrays"]}
            for view in c["pointer_views"]:
                self.assertIn(view["base"], names)
                self.assertNotIn(view["name"], names)
                self.assertNotIn(f"*{view['name']},", self.cases[name]["signature"])
            self.assertIn("may overlap", c["aliasing"])
            code = without_comments((self.output / f"kernels/{name}.c").read_text())
            self.assertNotIn("restrict", code)
        code = driver([self.cases["s424"]], [0, 1, 66], 8, 42)
        self.assertIn("got_array = make_input(n + 63", code)
        self.assertNotIn("got_xx", code)
        self.assertIn('compare("s424", "array"', code)
        ref = (self.output / "reference/s424.c").read_text()
        self.assertIn("static int *xx;", ref)
        self.assertIn("xx = array + vl;", ref)
        self.assertIn("temp += xx[i];", ref)

    def test_postludes_initializers_and_pointer_setup_are_reviewed_exactly(self):
        for old, new in (("temp += xx[i];", "temp += array[i];"),
                         ("int vl = 63;", "int vl = 64;"),
                         ("xx = array + vl;", "xx = array + 64;"),
                         ("set1d(xx, 0., 1);", "set1d(xx, 1., 1);")):
            with self.assertRaises(ValueError):
                extract_computation(self.funcs["s424"][2].replace(old, new), SPECS["s424"])
        case = self.cases["s424"]
        self.assertEqual(case["contract"]["removed_benchmark_initializers"], ["set1d(xx, 0., 1);"])
        self.assertEqual(case["contract"]["scalar_output"]["source_variable"], "temp")
        self.assertEqual(case["contract"]["scalar_output"]["observation"], "postlude")
        with self.assertRaises(ValueError):
            KernelSpec(read="a", views=(PointerView("xx", "a", "0", "xx = a;", "write"),))
        with self.assertRaises(ValueError):
            KernelSpec(result="sum", result_source="postlude")

    def test_pointer_induction_and_no_argument_helper_remain_explicit(self):
        code = without_comments((self.output / "kernels/s1351.c").read_text())
        self.assertIn("const int *B = b;", code)
        self.assertIn("*A = *B+*C;", code)
        self.assertIn("A++;", code)
        self.assertNotIn("restrict", code)
        helper = (self.output / "kernels/s471.c").read_text()
        self.assertIn("static int tsvc_s471s(void)", helper)
        self.assertIn("tsvc_s471s();", helper)
        self.assertIn("checksum += x[i];", helper)
        self.assertNotIn("set1d(", helper)

    def test_strided_offset_and_selector_contracts(self):
        a = self.cases["s171"]["contract"]["arrays"][0]
        self.assertEqual(a["layout"], "strided_vector")
        self.assertEqual(a["minimum_elements"], "max(1, n*inc)")
        self.assertEqual(self.cases["s162"]["contract"]["arrays"][0]["minimum_elements"], "max(1, n+max(0,k))")
        self.assertEqual(self.cases["s175"]["contract"]["arrays"][0]["minimum_elements"], "max(1, n+inc)")
        self.assertFalse(self.cases["s222"]["testing"]["contract_restriction"])
        self.assertTrue(all("value_domain" not in a for a in self.cases["s222"]["contract"]["arrays"]))
        selectors = self.cases["s442"]["contract"]["arrays"][-1]
        self.assertEqual(selectors["name"], "indx")
        self.assertNotIn("index_domain", selectors)
        self.assertEqual(selectors["selector_domain"]["default"], "fall through to case 1")
        code = driver([self.cases["s442"]], [1, 9], 12, 1)
        self.assertIn(f"index_pattern < {len(SELECTOR_PATTERNS)}", code)
        self.assertIn("fill_selectors(got_indx, index_pattern)", code)
        code = driver([self.cases["s162"], self.cases["s171"]], [0, 3], 12, 1)
        self.assertIn("make_input(n + (scalar_k > 0 ? scalar_k : 0)", code)
        self.assertIn("make_input(n * scalar_inc", code)
        with self.assertRaises(ValueError):
            KernelSpec(update="a", scalars=("k",), scalar_domains=(("k", "signed_offset"),), offset_vectors=(("a", "k"),))

    def compile_and_run(self, stem, source, names=()):
        cfile, binary = self.root / f"{stem}.c", self.root / stem
        cfile.write_text(source)
        flags = ["clang", "-std=c11", "-O2", "-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
        command = flags + ["-I", str(self.output), str(cfile),
                           *(str(self.output / f"kernels/{name}.c") for name in names), "-o", str(binary)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_overlap_and_post_loop_sums(self):
        self.compile_and_run("alias-values", r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int a[5]={10,20,30,40,50}, xx[3]={1,2,3};
    assert(s421(a,xx,3)==38 && xx[0]==12 && xx[1]==23 && xx[2]==3);
    assert(s421(a,xx,0)==0 && xx[0]==12);
    int b[5]={1,2,3,4,5};
    assert(s1421(a,b,5)==7);
    assert(b[0]==13 && b[1]==24 && b[2]==3 && b[3]==4 && b[4]==5);
    int anti[11]; for(int i=0;i<11;++i) anti[i]=i;
    assert(s422(a,anti,3)==87);
    assert(anti[4]==18 && anti[5]==29 && anti[6]==40 && anti[7]==7 && anti[10]==10);
    int ahead[67]; for(int i=0;i<67;++i) ahead[i]=i;
    assert(s423(a,ahead,3)==159);
    assert(ahead[0]==0 && ahead[1]==74 && ahead[2]==85 && ahead[3]==3 && ahead[66]==66);
    int ones[66], overlap[129];
    for(int i=0;i<66;++i) ones[i]=1;
    for(int i=0;i<129;++i) overlap[i]=1;
    assert(s424(ones,overlap,66)==132);
    assert(overlap[63]==1 && overlap[64]==2 && overlap[127]==2 && overlap[128]==3);
    int single[64]; for(int i=0;i<64;++i) single[i]=100+i;
    assert(s424(a,single,1)==163 && single[63]==163);
    assert(s424(a,single,0)==0 && single[63]==163);
    int out[3]={0}, left[3]={2,4,6}, right[3]={7,8,9};
    s1351(out,left,right,3);
    assert(out[0]==9 && out[1]==12 && out[2]==15);
    s1351(out,left,right,0);
    assert(out[0]==9 && out[2]==15);
    int hb[2]={1,2}, hc[2]={3,4}, hd[2]={2,3}, he[2]={5,6}, hx[2]={91,92};
    assert(s471(hb,hc,hd,he,hx,2)==16);
    assert(hb[0]==13 && hb[1]==22 && hx[0]==5 && hx[1]==11);
    return 0;
}
''', ["s421", "s1421", "s422", "s423", "s424", "s1351", "s471"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_hand_computed_symbolics_and_threshold_branches(self):
        start, step = self.cases["s122"]["contract"]["scalar_inputs"]
        samples = f"#define TEST_START ({scalar_test_value(start)})\n#define TEST_STEP ({scalar_test_value(step)})\n"
        self.compile_and_run("symbolic-values", samples + r'''
#include <assert.h>
#include <limits.h>
#include "kernels.h"
int main(void) {
    {
        int n=9, seen[4][3]={0};
        for(int trial=0;trial<12;++trial) {
            int start=TEST_START, step=TEST_STEP;
            int row=start==1 ? 0 : start==n+1 ? 1 : start==n ? 2 : 3;
            int col=step==1 ? 0 : step==2 ? 1 : 2;
            assert(!seen[row][col]++);
        }
        for(int i=0;i<4;++i) for(int j=0;j<3;++j) assert(seen[i][j]==1);
    }
    int a[7]={0}, b[7]={1,2,3,4,5,6,7};
    s122(a,b,2,2,7);
    assert(a[0]==0 && a[1]==7 && a[3]==6 && a[5]==5 && a[6]==0);
    s172(a,b,8,1,7);
    assert(a[1]==7 && a[3]==6 && a[5]==5);
    int huge_step[3]={0}, hb[3]={1,2,3};
    s122(huge_step,hb,1,INT_MAX-3,3);
    assert(huge_step[0]==3 && huge_step[1]==0 && huge_step[2]==0);
    int shifted[5]={10,20,30,40,50}, c[3]={2,2,2};
    s162(shifted,hb,c,2,3);
    assert(shifted[0]==32 && shifted[1]==44 && shifted[2]==30 && shifted[4]==50);
    s162(shifted,hb,c,INT_MIN,3);
    assert(shifted[0]==32 && shifted[1]==44);
    int strided[6]={10,11,12,13,14,15};
    s171(strided,hb,2,3);
    assert(strided[0]==11 && strided[1]==11 && strided[2]==14 && strided[4]==17 && strided[5]==15);
    int zero_stride[1]={10};
    s171(zero_stride,hb,0,3);
    assert(zero_stride[0]==16);
    s171(zero_stride,hb,INT_MAX,0);
    assert(zero_stride[0]==16);
    int lookahead[8]={10,20,30,40,50,60,70,80}, lb[5]={1,2,3,4,5};
    s175(lookahead,lb,3,5);
    assert(lookahead[0]==41 && lookahead[3]==74 && lookahead[4]==50 && lookahead[7]==80);
    int halves[7]={10,20,30,40,50,60,70};
    s174(halves,b,3,7);
    assert(halves[0]==10 && halves[3]==11 && halves[4]==22 && halves[5]==33 && halves[6]==70);
    for(int n=10;n<=11;++n) {
        int ta[11],tb[11],tc[11],td[11],te[11];
        for(int i=0;i<11;++i) { ta[i]=2;tb[i]=1;tc[i]=7;td[i]=2;te[i]=3; }
        s2710(ta,tb,tc,td,te,1,n);
        for(int i=0;i<n;++i) assert(tc[i]==(n==10 ? 7 : 11));
    }
    return 0;
}
''', ["s122", "s172", "s162", "s171", "s175", "s174", "s2710"])

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_selector_defaults_and_squared_recurrence_profile(self):
        self.compile_and_run("selector-values", DRIVER_SUPPORT + r'''
#include <assert.h>
#include "kernels.h"
int main(void) {
    int selectors[9]={1,2,3,4,0,-1,5,INT_MIN,INT_MAX};
    int a[9]={0}, b[9], c[9], d[9], e[9];
    for(int i=0;i<9;++i) { b[i]=2; c[i]=3; d[i]=4; e[i]=5; }
    s442(a,b,c,d,e,selectors,9);
    assert(a[0]==4 && a[1]==9 && a[2]==16 && a[3]==25);
    for(int i=4;i<9;++i) assert(a[i]==4);
    rng_state=42;
    for(int n=0;n<=128;++n) {
        Buffer input=make_input(n,9,0);
        prepare_squares(input,n);
        int64_t last=input.data[0];
        for(int i=1;i<n;++i) { last*=last; assert(last<=INT_MAX); }
        free(input.base);
    }
    int squared[5]={3,0,0,0,0}, zero[5]={0}, ba[5]={0}, ca[5]={0};
    s222(zero,ba,ca,squared,5);
    assert(squared[1]==9 && squared[2]==81 && squared[3]==6561 && squared[4]==43046721);
    return 0;
}
''', ["s442", "s222"])

    def candidate(self, name, transform, **kwargs):
        directory = Path(tempfile.mkdtemp(prefix=f"bad-{name}-", dir=self.root))
        original = (self.output / f"kernels/{name}.c").read_text()
        changed = transform(original)
        self.assertNotEqual(original, changed)
        (directory / f"{name}.c").write_text(changed)
        report = run_checks(self.output, names=[name], candidate_dir=directory, sanitize=True, **kwargs)
        self.assertEqual(report["status"], "failed")
        return report["error"]

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_snapshotting_the_overlapping_input_is_rejected(self):
        def snapshot(code):
            return (code.replace("#include <limits.h>", "#include <limits.h>\n#include <stdlib.h>")
                    .replace("int *xx;", "int *xx;\nint *saved = malloc((size_t)(n+63)*sizeof(int));\n"
                             "for(int i=0;i<n+63;++i) saved[i]=array[i];")
                    .replace("array[i] + a[i]", "saved[i] + a[i]")
                    .replace("return checksum;", "free(saved); return checksum;"))
        error = self.candidate("s424", snapshot, sizes=[66], trials=2)
        self.assertIn("s424: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_summing_the_wrong_half_is_rejected(self):
        error = self.candidate("s1421", lambda s: s.replace("checksum += xx[i];", "checksum += b[i];"), sizes=[5], trials=2)
        self.assertIn("s1421: scalar", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_unwritten_extended_tail_is_checked(self):
        error = self.candidate("s422", lambda s: s.replace("return checksum;", "array[n+7] = 42; return checksum;"),
                               sizes=[3], trials=1)
        self.assertIn("s422: array[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_fourth_selector_branch_and_default_are_checked(self):
        for old, new in (("case 4:  goto L40;", "case 4:  goto L15;"),
                         ("case 4:  goto L40;", "case 4:  goto L40; default: goto L40;")):
            error = self.candidate("s442", lambda s: s.replace(old, new), sizes=[3, 9], trials=8)
            self.assertIn("s442: a[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_ten_element_threshold_is_checked_by_default_sizes(self):
        error = self.candidate("s2710", lambda s: s.replace("n > 10", "n > 9"), trials=8)
        self.assertIn("s2710: c[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_distinct_scalar_parameters_are_not_interchangeable(self):
        error = self.candidate("s242", lambda s: s.replace("+ s1 + s2 +", "+ s1 + s1 +"), sizes=[2], trials=2)
        self.assertIn("s242: a[", error)

    @unittest.skipUnless(shutil.which("clang"), "requires clang")
    def test_schema_four_scalar_slots_still_run(self):
        directory = self.root / "schema-four"
        case = self.cases["s3110"]
        for kind in ("kernel", "reference"):
            destination = directory / case[kind]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.output / case[kind], destination)
        (directory / "manifest.json").write_text(json.dumps({
            "schema_version": 4, "source_sha256": self.manifest["source_sha256"], "cases": [case]}))
        report = run_checks(directory, matrix_sizes=[1,3], trials=8, sanitize=True)
        self.assertEqual(report["status"], "passed_differential_tests", report.get("error"))


if __name__ == "__main__":
    unittest.main()
