/* TSVC integer adaptation: s272 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s272.json for the complete contract and adaptations.
 * Source SHA256: ae97e6c856769ae21b64195c05393753f3aa2e5692f9f1941de70e37080f162d
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s272(int *a, int *b, const int *c, const int *d, const int *e, int t, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (e[i] >= t) {
                a[i] += c[i] * d[i];
                b[i] += c[i] * c[i];
            }
        }
    }
}
