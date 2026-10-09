/* TSVC integer adaptation: s278 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s278.json for the complete contract and adaptations.
 * Source SHA256: 316ff9ea2d20e9fc7fbc3cf4274c186dcc6b65e1b0d78568663c81370a27d213
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s278(int *a, int *b, int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
                    if (a[i] > (int)0) {
                        goto L20;
                    }
                    b[i] = -b[i] + d[i] * e[i];
                    goto L30;
        L20:
                    c[i] = -c[i] + d[i] * e[i];
        L30:
                    a[i] = b[i] + c[i] * d[i];
                }
    }
}
