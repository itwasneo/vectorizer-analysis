/* TSVC integer adaptation: s323 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s323.json for the complete contract and adaptations.
 * Source SHA256: f00a2684d2d3698a25a2b8d97412b2bb40862e78fe611cd840714c228ea933f0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s323(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 1; i < n; i++) {
            a[i] = b[i-1] + c[i] * d[i];
            b[i] = a[i] + c[i] * e[i];
        }
    }
}
