/* TSVC integer adaptation: vtv (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vtv.json for the complete contract and adaptations.
 * Source SHA256: c06f8606dd48cad144a1a7e3287bdea97e2af9918f65825a24479663007ffa08
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vtv(int *a, const int *b, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] *= b[i];
        }
    }
}
