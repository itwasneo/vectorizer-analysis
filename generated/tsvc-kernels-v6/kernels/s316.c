/* TSVC integer adaptation: s316 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s316.json for the complete contract and adaptations.
 * Source SHA256: d6acf36925e9cdbcf6312b8b82f83e48fc5ca5d30a7e884867f2502135713e99
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s316(const int *a, int n) {
    int x;
    {
        x = a[0];
        for (int i = 1; i < n; ++i) {
            if (a[i] < x) {
                x = a[i];
            }
        }
    }
    return x;
}
