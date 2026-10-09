/* TSVC integer adaptation: s1161 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1161.json for the complete contract and adaptations.
 * Source SHA256: cac480527e72534cee331ac732c47159c554641224070c7c40e1c566c9588e0f
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1161(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n-1; ++i) {
                    if (c[i] < (int)0) {
                        goto L20;
                    }
                    a[i] = c[i] + d[i] * e[i];
                    goto L10;
        L20:
                    b[i] = a[i] + d[i] * d[i];
        L10:
                    ;
                }
    }
}
