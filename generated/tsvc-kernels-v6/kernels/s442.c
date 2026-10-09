/* TSVC integer adaptation: s442 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: read, e: read, indx: read. Each has at least max(1,n) initialized ints.
 * indx selectors may be any int; values outside 1..4 use the case-1 computation.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s442.json for the complete contract and adaptations.
 * Source SHA256: b0affb48f4fad177c7a04038136a2ee5eed2cd1b05a399ae086ecebe23b11ebe
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s442(int *a, const int *b, const int *c, const int *d, const int *e, const int *indx, int n) {
    {
        for (int i = 0; i < n; i++) {
                    switch (indx[i]) {
                        case 1:  goto L15;
                        case 2:  goto L20;
                        case 3:  goto L30;
                        case 4:  goto L40;
                    }
        L15:
                    a[i] += b[i] * b[i];
                    goto L50;
        L20:
                    a[i] += c[i] * c[i];
                    goto L50;
        L30:
                    a[i] += d[i] * d[i];
                    goto L50;
        L40:
                    a[i] += e[i] * e[i];
        L50:
                    ;
                }
    }
}
