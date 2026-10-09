/* TSVC integer adaptation: s275 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read, cc: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s275.json for the complete contract and adaptations.
 * Source SHA256: 598660b046f6e3c4359d3ec8f0236033c00431e8027aaa4de19b079299b98794
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s275(int *aa, const int *bb, const int *cc, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            if (aa[(size_t)(0) * ld + (i)] > (int)0) {
                for (int j = 1; j < n; j++) {
                    aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j-1) * ld + (i)] + bb[(size_t)(j) * ld + (i)] * cc[(size_t)(j) * ld + (i)];
                }
            }
        }
    }
}
