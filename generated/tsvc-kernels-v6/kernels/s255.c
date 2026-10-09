/* TSVC integer adaptation: s255 (one computational repetition).
 * Contract: 2 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s255.json for the complete contract and adaptations.
 * Source SHA256: 7af2cb9b8c3cf16a912805674781e8e10fab39efc00fdfe78319166a6b1f72e6
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s255(int *a, const int *b, int n) {
    int x, y;
    {
        x = b[n-1];
        y = b[n-2];
        for (int i = 0; i < n; i++) {
            a[i] = (b[i] + x + y) * (int)0;
            y = x;
            x = b[i];
        }
    }
}
