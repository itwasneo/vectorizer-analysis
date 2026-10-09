/* TSVC integer adaptation: s291 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s291.json for the complete contract and adaptations.
 * Source SHA256: 69485ec4880d840f1f721371c4b6f0e904d5a562aaf391ca170be0a456773df0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s291(int *a, const int *b, int n) {
    int im1;
    {
        im1 = n-1;
        for (int i = 0; i < n; i++) {
            a[i] = (b[i] + b[im1]) * (int)0;
            im1 = i;
        }
    }
}
