/* TSVC integer adaptation: s141 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: array: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s141.json for the complete contract and adaptations.
 * Source SHA256: 1fa5b1fbc418aef91f7692f7c0b7a7dfeff4cd38b9b561007f929376c9e688f7
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s141(int *array, const int *bb, int n, int ld) {
    int k;
    {
        for (int i = 0; i < n; i++) {
            k = (i+1) * ((i+1) - 1) / 2 + (i+1)-1;
            for (int j = i; j < n; j++) {
                array[k] += bb[(size_t)(j) * ld + (i)];
                k += j+1;
            }
        }
    }
}
