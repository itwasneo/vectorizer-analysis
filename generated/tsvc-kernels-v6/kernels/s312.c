/* TSVC integer adaptation: s312 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s312.json for the complete contract and adaptations.
 * Source SHA256: 784428ac2d195d570652bd17ebf5b4a99838c59f8b8bb14a6fe9a4bc227c0ce7
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s312(const int *a, int n) {
    int prod;
    {
        prod = (int)1;
        for (int i = 0; i < n; i++) {
            prod *= a[i];
        }
    }
    return prod;
}
