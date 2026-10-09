/* TSVC integer adaptation: s162 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * a instead requires max(1,n+max(0,k)) initialized ints.
 * Scalar contract: INT_MIN <= k <= INT_MAX-n.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s162.json for the complete contract and adaptations.
 * Source SHA256: 52c54c4547994e4cc473c545bcaba05bd0d55c8380bef2bfab6e41cdd32c2d3f
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s162(int *a, const int *b, const int *c, int k, int n) {
    {
        if (k > 0) {
            for (int i = 0; i < n-1; i++) {
                a[i] = a[i + k] + b[i] * c[i];
            }
        }
    }
}
