/* TSVC integer adaptation: s311 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s311.json for the complete contract and adaptations.
 * Source SHA256: 8b036e883a7d438c8ee1951ed0ea8941591ac999af680680ccb99f8b48f967ab
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s311(const int *a, int n) {
    int sum;
    {
        sum = (int)0;
        for (int i = 0; i < n; i++) {
            sum += a[i];
        }
    }
    return sum;
}
