/* TSVC integer adaptation: s115 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, aa: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s115.json for the complete contract and adaptations.
 * Source SHA256: adaa11659e2ff5e8eb2124501e15ee09f93f15cac996f24d621809ef57f7b303
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s115(int *a, const int *aa, int n, int ld) {
    {
        for (int j = 0; j < n; j++) {
            for (int i = j+1; i < n; i++) {
                a[i] -= aa[(size_t)(j) * ld + (i)] * a[j];
            }
        }
    }
}
