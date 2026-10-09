/* TSVC integer adaptation: vpvtv (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vpvtv.json for the complete contract and adaptations.
 * Source SHA256: f2fb847a4cc1b23adcdbab2504b248a3d13105095d2e8fd5fbc5aa3e81c26fa1
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vpvtv(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i] * c[i];
        }
    }
}
