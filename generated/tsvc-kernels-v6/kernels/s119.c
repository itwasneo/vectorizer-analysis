/* TSVC integer adaptation: s119 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s119.json for the complete contract and adaptations.
 * Source SHA256: 81718ce46eefa0d3109aa568d00d80b969fe03209c615cd8eef1889dfcff7b2a
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s119(int *aa, const int *bb, int n, int ld) {
    {
        for (int i = 1; i < n; i++) {
            for (int j = 1; j < n; j++) {
                aa[(size_t)(i) * ld + (j)] = aa[(size_t)(i-1) * ld + (j-1)] + bb[(size_t)(i) * ld + (j)];
            }
        }
    }
}
