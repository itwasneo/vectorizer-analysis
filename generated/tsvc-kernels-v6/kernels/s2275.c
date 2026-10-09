/* TSVC integer adaptation: s2275 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: write, aa: read_write, b: read, bb: read, c: read, cc: read, d: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2275.json for the complete contract and adaptations.
 * Source SHA256: 5d96354df6e9de395d734ce21e94facd8a8e0434286921c9db87fbe29a8656bb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s2275(int *a, int *aa, const int *b, const int *bb, const int *c, const int *cc, const int *d, int n, int ld) {
    {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j) * ld + (i)] + bb[(size_t)(j) * ld + (i)] * cc[(size_t)(j) * ld + (i)];
            }
            a[i] = b[i] + c[i] * d[i];
        }
    }
}
