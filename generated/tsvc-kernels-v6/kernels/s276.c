/* TSVC integer adaptation: s276 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s276.json for the complete contract and adaptations.
 * Source SHA256: 54bd67111ea6e5178fad056854440a6d182bfc1935130cde1bb90835a02c7954
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s276(int *a, const int *b, const int *c, const int *d, int n) {
    int mid = (n/2);
    {
        for (int i = 0; i < n; i++) {
            if (i+1 < mid) {
                a[i] += b[i] * c[i];
            } else {
                a[i] += b[i] * d[i];
            }
        }
    }
}
