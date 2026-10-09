/* TSVC integer adaptation: s343 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read, array: write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s343.json for the complete contract and adaptations.
 * Source SHA256: 755a03d3ce3ad0c95ebe7dd76146a689b594e1391f4ab2cff5a8d388a0ca1f62
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s343(const int *aa, int *array, const int *bb, int n, int ld) {
    int k;
    {
        k = -1;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (bb[(size_t)(j) * ld + (i)] > (int)0) {
                    k++;
                    array[k] = aa[(size_t)(j) * ld + (i)];
                }
            }
        }
    }
}
