/* TSVC integer adaptation: s222 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, e: read_write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s222.json for the complete contract and adaptations.
 * Source SHA256: 55d299de590ac13dd1a6116be85cc3211dd0a810d96415a38d2001678a2ae2ed
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s222(int *a, const int *b, const int *c, int *e, int n) {
    {
        for (int i = 1; i < n; i++) {
            a[i] += b[i] * c[i];
            e[i] = e[i - 1] * e[i - 1];
            a[i] -= b[i] * c[i];
        }
    }
}
