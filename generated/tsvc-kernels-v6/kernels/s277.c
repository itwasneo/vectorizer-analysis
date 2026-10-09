/* TSVC integer adaptation: s277 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s277.json for the complete contract and adaptations.
 * Source SHA256: 9599d754300b4448eb7d5e959c97110f6d5876243d6aa072490bc75675f85dc4
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s277(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n-1; i++) {
                        if (a[i] >= (int)0) {
                            goto L20;
                        }
                        if (b[i] >= (int)0) {
                            goto L30;
                        }
                        a[i] += c[i] * d[i];
        L30:
                        b[i+1] = c[i] + d[i] * e[i];
        L20:
        ;
                }
    }
}
