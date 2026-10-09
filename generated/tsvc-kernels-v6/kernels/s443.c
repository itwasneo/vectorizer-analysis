/* TSVC integer adaptation: s443 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s443.json for the complete contract and adaptations.
 * Source SHA256: 8cb5f152f770f57fe951f2a88bdd9f7be4960c7634b866ed0dab4c9503f39e41
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s443(int *a, const int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n; i++) {
                    if (d[i] <= (int)0) {
                        goto L20;
                    } else {
                        goto L30;
                    }
        L20:
                    a[i] += b[i] * c[i];
                    goto L50;
        L30:
                    a[i] += b[i] * b[i];
        L50:
                    ;
                }
    }
}
