/* TSVC integer adaptation: s451 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Mixed numeric computation: double sin/cos and addition, then truncate to int; link libm, no fast-math.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s451.json for the complete contract and adaptations.
 * Source SHA256: bf6a455c5425d225d6e23ee57b62c63a9778309d1cacbc225afd5d21a0f42669
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <math.h>
#include <float.h>
_Static_assert(FLT_RADIX == 2 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024 && FLT_EVAL_METHOD == 0, "Requires binary64 evaluation");
#ifdef __FAST_MATH__
#error "s451 requires strict math"
#endif

void s451(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
        a[i] = sin(b[i]) + cos(c[i]);
                }
    }
}
