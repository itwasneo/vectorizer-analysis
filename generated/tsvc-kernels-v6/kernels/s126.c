/* TSVC integer adaptation: s126 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: array: read, bb: read_write, cc: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s126.json for the complete contract and adaptations.
 * Source SHA256: 694b471f1bd67d945d3f4a79d77409fa782a4eb1193b2f8e2e3a571dba1033df
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s126(const int *array, int *bb, const int *cc, int n, int ld) {
    int k;
    {
        k = 1;
        for (int i = 0; i < n; i++) {
            for (int j = 1; j < n; j++) {
                bb[(size_t)(j) * ld + (i)] = bb[(size_t)(j-1) * ld + (i)] + array[k-1] * cc[(size_t)(j) * ld + (i)];
                ++k;
            }
            ++k;
        }
    }
}
