/* TSVC integer adaptation: s314 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s314.json for the complete contract and adaptations.
 * Source SHA256: 9919b8b90834b08bb40382452fd68593f418a642a120623c9d4a046ce4003e39
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s314(const int *a, int n) {
    int x;
    {
        x = a[0];
        for (int i = 0; i < n; i++) {
            if (a[i] > x) {
                x = a[i];
            }
        }
    }
    return x;
}
