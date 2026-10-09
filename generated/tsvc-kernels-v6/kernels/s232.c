/* TSVC integer adaptation: s232 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s232.json for the complete contract and adaptations.
 * Source SHA256: cc8b4a9a64f7f07d1046f9a9ce212c5c9daa7ba83499bb5509936234ce35980a
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s232(int *aa, const int *bb, int n, int ld) {
    {
        for (int j = 1; j < n; j++) {
            for (int i = 1; i <= j; i++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j) * ld + (i-1)]*aa[(size_t)(j) * ld + (i-1)]+bb[(size_t)(j) * ld + (i)];
            }
        }
    }
}
