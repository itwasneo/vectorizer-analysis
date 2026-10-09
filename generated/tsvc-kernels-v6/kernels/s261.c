/* TSVC integer adaptation: s261 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read_write, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s261.json for the complete contract and adaptations.
 * Source SHA256: 742a3ae48647a25840f8c3da786c6a1d09e0ee7ac0e8483270022ef3c0c07654
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s261(int *a, const int *b, int *c, const int *d, int n) {
    int t;
    {
        for (int i = 1; i < n; ++i) {
            t = a[i] + b[i];
            a[i] = t + c[i-1];
            t = c[i] * d[i];
            c[i] = t;
        }
    }
}
