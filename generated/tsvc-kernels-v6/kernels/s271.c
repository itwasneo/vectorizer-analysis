/* TSVC integer adaptation: s271 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s271.json for the complete contract and adaptations.
 * Source SHA256: 543d67e67881c17a271b29403cac982a95b520a4d88b0bc403b780971bc54c9e
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s271(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (b[i] > (int)0) {
                a[i] += b[i] * c[i];
            }
        }
    }
}
