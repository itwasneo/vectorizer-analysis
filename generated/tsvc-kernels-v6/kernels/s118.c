/* TSVC integer adaptation: s118 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s118.json for the complete contract and adaptations.
 * Source SHA256: d48bfc3d5b7e2d040d32eb358555a4136cdfecdf818ecd0a36223ce62db32e0b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s118(int *a, const int *bb, int n, int ld) {
    {
        for (int i = 1; i < n; i++) {
            for (int j = 0; j <= i - 1; j++) {
                a[i] += bb[(size_t)(j) * ld + (i)] * a[i-j-1];
            }
        }
    }
}
