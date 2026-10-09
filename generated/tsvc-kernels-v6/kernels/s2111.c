/* TSVC integer adaptation: s2111 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read_write. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2111.json for the complete contract and adaptations.
 * Source SHA256: 97d3c1cebf35920bae0cd73ffbf37adda60e513e4fe2b88964e238fe69e39700
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

int s2111(int *aa, int n, int ld) {
    int checksum;
    {
        for (int j = 1; j < n; j++) {
            for (int i = 1; i < n; i++) {
                aa[(size_t)(j) * ld + (i)] = aa[(size_t)(j) * ld + (i-1)] + aa[(size_t)(j-1) * ld + (i)];
            }
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                checksum += aa[(size_t)(i) * ld + (j)];
        if (checksum == 0) checksum = 3;
    return checksum;
}
