/* TSVC integer adaptation: s292 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Excluded sizes: 1.
 * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s292.json for the complete contract and adaptations.
 * Source SHA256: 57da54cc64428ab21f8b4cfc8775269aa0121e059bb929fb928f4313e32435d6
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s292(int *a, const int *b, int n) {
    int im1, im2;
    {
        im1 = n-1;
        im2 = n-2;
        for (int i = 0; i < n; i++) {
            a[i] = (b[i] + b[im1] + b[im2]) * (int)0;
            im2 = im1;
            im1 = i;
        }
    }
}
