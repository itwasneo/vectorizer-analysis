/* TSVC integer adaptation: s257 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, aa: read_write, bb: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s257.json for the complete contract and adaptations.
 * Source SHA256: 946aadae8b0412fec86df2ae85fbc416e3e2388dc7876b7de90724ab136342a0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s257(int *a, int *aa, const int *bb, int n, int ld) {
    {
        for (int i = 1; i < n; i++) {
            for (int j = 0; j < n; j++) {
                a[i] = aa[(size_t)(j) * ld + (i)] - a[i-1];
                aa[(size_t)(j) * ld + (i)] = a[i] + bb[(size_t)(j) * ld + (i)];
            }
        }
    }
}
