/* TSVC integer adaptation: vsumr (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vsumr.json for the complete contract and adaptations.
 * Source SHA256: 914002be0beda376c1d13ce65d7b8d21300b4b21d6aa9ac6c838c7c703c2f358
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int vsumr(const int *a, int n) {
    int sum;
    {
        sum = 0;
        for (int i = 0; i < n; i++) {
            sum += a[i];
        }
    }
    return sum;
}
