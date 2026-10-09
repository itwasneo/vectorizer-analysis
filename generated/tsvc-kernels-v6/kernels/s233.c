/* TSVC integer adaptation: s233 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, bb: read_write, cc: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s233.json for the complete contract and adaptations.
 * Source SHA256: a1ac30e32924336fa73bf18949f10ff299dfdf70105c1c2ee89c2719a274f41b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s233(int *aa, int *bb, const int *cc, int n, int ld) {
    {
        for (int i = 1; i < n; i++) {
            for (int j = 1; j < n; j++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j-1) * ld + (i)] + cc[(size_t)(j) * ld + (i)];
            }
            for (int j = 1; j < n; j++) {
                bb[(size_t)(j) * ld + (i)] = bb[(size_t)(j) * ld + (i-1)] + cc[(size_t)(j) * ld + (i)];
            }
        }
    }
}
