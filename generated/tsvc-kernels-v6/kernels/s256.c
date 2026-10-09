/* TSVC integer adaptation: s256 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, bb: read, cc: write, d: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s256.json for the complete contract and adaptations.
 * Source SHA256: 178e2adbe9d3c92e1980b39372676a7145624b0c7401dc9780fdea390593cfaf
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s256(int *a, const int *bb, int *cc, const int *d, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            for (int j = 1; j < n; j++) {
                a[j] = (int)1 - a[j - 1];
                cc[(size_t)(j) * ld + (i)] = a[j] + bb[(size_t)(j) * ld + (i)]*d[j];
            }
        }
    }
}
