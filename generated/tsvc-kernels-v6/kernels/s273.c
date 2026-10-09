/* TSVC integer adaptation: s273 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s273.json for the complete contract and adaptations.
 * Source SHA256: 284b21f5dbc729c877dde84a262dd88c61298e14404d84e8e5374db39ce4ca86
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s273(int *a, int *b, int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += d[i] * e[i];
            if (a[i] < (int)0)
                b[i] += d[i] * e[i];
            c[i] += a[i] * d[i];
        }
    }
}
