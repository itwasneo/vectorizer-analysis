/* TSVC integer adaptation: s176 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s176.json for the complete contract and adaptations.
 * Source SHA256: 5071c72ea681c4166259d71aeb7c2e641b92f38060e8804f5cf04863b3c21636
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s176(int *a, const int *b, const int *c, int n) {
    int m = n/2;
    {
        for (int j = 0; j < (n/2); j++) {
            for (int i = 0; i < m; i++) {
                a[i] += b[i+m-j-1] * c[j];
            }
        }
    }
}
