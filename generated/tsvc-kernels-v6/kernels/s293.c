/* TSVC integer adaptation: s293 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s293.json for the complete contract and adaptations.
 * Source SHA256: 11fc364f9b8a4240b34366227ec08538df5b75da33a8bffb7aae808390600d49
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s293(int *a, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = a[0];
        }
    }
}
