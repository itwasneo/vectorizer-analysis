/* TSVC integer adaptation: s235 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, aa: read_write, b: read, bb: read, c: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s235.json for the complete contract and adaptations.
 * Source SHA256: 3e2008e9094a4b435275ac7e4faae3620a007ccc48fb3710ed6fdf3e279ffe9b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s235(int *a, int *aa, const int *b, const int *bb, const int *c, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i] * c[i];
            for (int j = 1; j < n; j++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j-1) * ld + (i)] + bb[(size_t)(j) * ld + (i)] * a[i];
            }
        }
    }
}
