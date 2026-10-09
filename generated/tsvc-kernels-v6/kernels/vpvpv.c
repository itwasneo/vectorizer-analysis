/* TSVC integer adaptation: vpvpv (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vpvpv.json for the complete contract and adaptations.
 * Source SHA256: d1ae4706e6106c312f7980eb7c44d1bef87630561e65c080daa7921ab03544f2
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vpvpv(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i] + c[i];
        }
    }
}
