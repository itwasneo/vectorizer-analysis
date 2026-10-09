/* TSVC integer adaptation: s000 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: X: write, Y: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s000.json for the complete contract and adaptations.
 * Source SHA256: d887ee52542d95c0a37e5915cd19a35b1d2876fdde1b90efee7622eac5d8fa5c
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s000(int *X, const int *Y, int n) {
    {
        for (int i = 0; i < n; i++) {
            X[i] = Y[i] + 1;
        }
    }
}
