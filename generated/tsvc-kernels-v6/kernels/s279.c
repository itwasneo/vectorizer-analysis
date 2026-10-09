/* TSVC integer adaptation: s279 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s279.json for the complete contract and adaptations.
 * Source SHA256: db97c9bacd6600f1b9c4e6d636ad900e1ac983e5055bd60237bcc3c6a4467aa0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s279(int *a, int *b, int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
                    if (a[i] > (int)0) {
                        goto L20;
                    }
                    b[i] = -b[i] + d[i] * d[i];
                    if (b[i] <= a[i]) {
                        goto L30;
                    }
                    c[i] += d[i] * e[i];
                    goto L30;
        L20:
                    c[i] = -c[i] + e[i] * e[i];
        L30:
                    a[i] = b[i] + c[i] * d[i];
                }
    }
}
