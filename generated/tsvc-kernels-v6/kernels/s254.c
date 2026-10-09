/* TSVC integer adaptation: s254 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s254.json for the complete contract and adaptations.
 * Source SHA256: 76c8ff5cb8845075d138837ea1e3bb5a1606a6375af942d79231de0384c94ea0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s254(int *a, const int *b, int n) {
    int x;
    {
        x = b[n-1];
        for (int i = 0; i < n; i++) {
            a[i] = (b[i] + x) * (int)0;
            x = b[i];
        }
    }
}
