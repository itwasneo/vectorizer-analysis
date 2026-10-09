/* TSVC integer adaptation: s242 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s242.json for the complete contract and adaptations.
 * Source SHA256: 64516cb41ce87566b8991281f9107efaf1273b3311958a9a2716b5fa12940aa8
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s242(int *a, const int *b, const int *c, const int *d, int s1, int s2, int n) {
    {
        for (int i = 1; i < n; ++i) {
            a[i] = a[i - 1] + s1 + s2 + b[i] + c[i] + d[i];
        }
    }
}
