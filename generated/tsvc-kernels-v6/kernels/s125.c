/* TSVC integer adaptation: s125 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read, array: write, bb: read, cc: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s125.json for the complete contract and adaptations.
 * Source SHA256: b5e5998f9e7c096ab8f95a0ba5013c01a8cc63eeb5e69095ee1b7a5bcb92d4fd
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s125(const int *aa, int *array, const int *bb, const int *cc, int n, int ld) {
    int k;
    {
        k = -1;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                k++;
                array[k] = aa[(size_t)(i) * ld + (j)] + bb[(size_t)(i) * ld + (j)] * cc[(size_t)(i) * ld + (j)];
            }
        }
    }
}
