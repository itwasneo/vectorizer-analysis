/* TSVC integer adaptation: s132 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write, b: read, c: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s132.json for the complete contract and adaptations.
 * Source SHA256: 22c647929b749f624f044362af5ff4e911913c7471097481523c6958f35bbf05
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s132(int *aa, const int *b, const int *c, int n, int ld) {
    int m = 0;
    int j = m;
    int k = m+1;
    {
        for (int i= 1; i < n; i++) {
            aa[(size_t)(j) * ld + (i)] = aa[(size_t)(k) * ld + (i-1)] + b[i] * c[1];
        }
    }
}
