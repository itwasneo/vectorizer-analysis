/* TSVC integer adaptation: s1244 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1244.json for the complete contract and adaptations.
 * Source SHA256: b33afa01c33b6b148d5bf82a639286db0e4aa7209adb7bd11bffd63891055290
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1244(int *a, const int *b, const int *c, int *d, int n) {
    {
        for (int i = 0; i < n-1; i++) {
            a[i] = b[i] + c[i] * c[i] + b[i]*b[i] + c[i];
            d[i] = a[i] + a[i+1];
        }
    }
}
