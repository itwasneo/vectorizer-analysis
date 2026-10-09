/* TSVC integer adaptation: s258 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, aa: read, b: write, c: read, d: read, e: write. Matrices are single rows: ld >= max(1,n), with ld initialized ints. Vectors use max(1,n).
 * ld*sizeof(int) must fit in SIZE_MAX; row padding is preserved. No cross-row access.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s258.json for the complete contract and adaptations.
 * Source SHA256: cee342628a2d6621cf7e9ea99feda0bee828f4436af0562a31bd00b24e17af91
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

void s258(const int *a, const int *aa, int *b, const int *c, const int *d, int *e, int n, int ld) {
    int s;
    {
        s = 0;
        for (int i = 0; i < n; ++i) {
            if (a[i] > 0) {
                s = d[i] * d[i];
            }
            b[i] = s * c[i] + d[i];
            e[i] = (s + (int)1) * aa[(size_t)(0) * ld + (i)];
        }
    }
}
