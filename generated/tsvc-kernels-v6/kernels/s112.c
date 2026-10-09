/* TSVC integer adaptation: s112 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s112.json for the complete contract and adaptations.
 * Source SHA256: 95102cf45cc0f7a417e0829bada0cdeb68e31d6fa109ec06a5c7b60254991b07
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s112(int *a, const int *b, int n) {
    {
        for (int i = n - 2; i >= 0; i--) {
            a[i+1] = a[i] + b[i];
        }
    }
}
