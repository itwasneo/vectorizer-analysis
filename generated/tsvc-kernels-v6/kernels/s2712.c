/* TSVC integer adaptation: s2712 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2712.json for the complete contract and adaptations.
 * Source SHA256: e2d997773a806de9306c76b7fe58fb814ce6d794f467a5e7c24c795339ccb585
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s2712(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (a[i] > b[i]) {
                a[i] += b[i] * c[i];
            }
        }
    }
}
