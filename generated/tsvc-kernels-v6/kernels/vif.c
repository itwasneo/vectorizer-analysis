/* TSVC integer adaptation: vif (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vif.json for the complete contract and adaptations.
 * Source SHA256: 7c9fba9ba9debdf9ccc65c3da4b7a883a1deb25a3424c102b0527c7ae471f928
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vif(int *a, const int *b, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (b[i] > (int)0) {
                a[i] = b[i];
            }
        }
    }
}
