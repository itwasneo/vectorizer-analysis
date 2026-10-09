/* TSVC integer adaptation: s231 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s231.json for the complete contract and adaptations.
 * Source SHA256: 5f688e358be86ebd6589057de5760f58bd791a5fc59e9e847b95469d384b42cc
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s231(int *aa, const int *bb, int n, int ld) {
    {
        for (int i = 0; i < n; ++i) {
            for (int j = 1; j < n; j++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j - 1) * ld + (i)] + bb[(size_t)(j) * ld + (i)];
            }
        }
    }
}
