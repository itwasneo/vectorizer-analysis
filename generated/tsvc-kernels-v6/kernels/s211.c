/* TSVC integer adaptation: s211 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s211.json for the complete contract and adaptations.
 * Source SHA256: 1b3fac93f27ac087fa0e806cc1c34dbad641fcea26570779bf173d2e75b2f90a
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s211(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 1; i < n-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
            b[i] = b[i + 1] - e[i] * d[i];
        }
    }
}
