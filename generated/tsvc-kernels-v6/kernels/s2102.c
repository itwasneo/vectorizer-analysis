/* TSVC integer adaptation: s2102 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: write. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2102.json for the complete contract and adaptations.
 * Source SHA256: 66f520ae1a829e8c71f2059f498a7d549fea1cb6694e7554bdefeeca669fc484
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s2102(int *aa, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aa[(size_t)(j) * ld + (i)] = (int)0;
            }
            aa[(size_t)(i) * ld + (i)] = (int)1;
        }
    }
}
