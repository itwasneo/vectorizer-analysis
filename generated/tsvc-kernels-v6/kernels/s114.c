/* TSVC integer adaptation: s114 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s114.json for the complete contract and adaptations.
 * Source SHA256: 7dd4418a55d84b3a0a06f01330bd5a8c1f79735560aa38682baa6ec6cf6a14b6
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s114(int *aa, const int *bb, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < i; j++) {
                aa[(size_t)(i) * ld + (j)] = aa[(size_t)(j) * ld + (i)] + bb[(size_t)(i) * ld + (j)];
            }
        }
    }
}
