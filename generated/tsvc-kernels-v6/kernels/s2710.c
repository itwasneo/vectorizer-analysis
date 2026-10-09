/* TSVC integer adaptation: s2710 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2710.json for the complete contract and adaptations.
 * Source SHA256: 779cc6abe0ef48bec6f49a5ca1a9e990e43a6f17e972cf5967b60ca9316640aa
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s2710(int *a, int *b, int *c, const int *d, const int *e, int x, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (a[i] > b[i]) {
                a[i] += b[i] * d[i];
                if (n > 10) {
                    c[i] += d[i] * d[i];
                } else {
                    c[i] = d[i] * e[i] + (int)1;
                }
            } else {
                b[i] = a[i] + e[i] * e[i];
                if (x > (int)0) {
                    c[i] = a[i] + d[i] * d[i];
                } else {
                    c[i] += e[i] * e[i];
                }
            }
        }
    }
}
