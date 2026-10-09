/* TSVC integer adaptation: s161 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read_write, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s161.json for the complete contract and adaptations.
 * Source SHA256: dc2ddaca7209b0c699f34f5cd5ecc95d63ab200f5d978f028d396e61dc23672b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s161(int *a, const int *b, int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n-1; ++i) {
                    if (b[i] < (int)0) {
                        goto L20;
                    }
                    a[i] = c[i] + d[i] * e[i];
                    goto L10;
        L20:
                    c[i+1] = a[i] + d[i] * d[i];
        L10:
                    ;
                }
    }
}
