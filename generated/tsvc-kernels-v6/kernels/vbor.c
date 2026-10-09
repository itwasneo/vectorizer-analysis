/* TSVC integer adaptation: vbor (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, aa: read, b: read, c: read, d: read, e: read, x: write. Matrices are single rows: ld >= max(1,n), with ld initialized ints. Vectors use max(1,n).
 * ld*sizeof(int) must fit in SIZE_MAX; row padding is preserved. No cross-row access.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vbor.json for the complete contract and adaptations.
 * Source SHA256: c2e9b6daf9a2342bb0e12d67e1d3990d5ac8cd820d69d63fde6debee29b755dd
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

int vbor(const int *a, const int *aa, const int *b, const int *c, const int *d, const int *e, int *x, int n, int ld) {
    int checksum;
    int a1, b1, c1, d1, e1, f1;
    {
        for (int i = 0; i < n; i++) {
            a1 = a[i];
            b1 = b[i];
            c1 = c[i];
            d1 = d[i];
            e1 = e[i];
            f1 = aa[(size_t)(0) * ld + (i)];
            a1 = a1 * b1 * c1 + a1 * b1 * d1 + a1 * b1 * e1 + a1 * b1 * f1 +
                a1 * c1 * d1 + a1 * c1 * e1 + a1 * c1 * f1 + a1 * d1 * e1
                + a1 * d1 * f1 + a1 * e1 * f1;
            b1 = b1 * c1 * d1 + b1 * c1 * e1 + b1 * c1 * f1 + b1 * d1 * e1 +
                b1 * d1 * f1 + b1 * e1 * f1;
            c1 = c1 * d1 * e1 + c1 * d1 * f1 + c1 * e1 * f1;
            d1 = d1 * e1 * f1;
            x[i] = a1 * b1 * c1 * d1;
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++){
            checksum += x[i];
        }
    return checksum;
}
