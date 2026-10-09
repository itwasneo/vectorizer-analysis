/* TSVC integer adaptation: s1279 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1279.json for the complete contract and adaptations.
 * Source SHA256: a64f14ec18139a71f129396abdb749ef628e5ce45b56ce2ed784dc9bea3a4a82
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1279(const int *a, const int *b, int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (a[i] < (int)0) {
                if (b[i] > a[i]) {
                    c[i] += d[i] * e[i];
                }
            }
        }
    }
}
