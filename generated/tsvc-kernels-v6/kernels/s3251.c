/* TSVC integer adaptation: s3251 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: write, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s3251.json for the complete contract and adaptations.
 * Source SHA256: 7dfdee9f0fe6c1c543061984d820abd6761e99302fcd6157d14730e6a953bb6b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s3251(int *a, int *b, const int *c, int *d, const int *e, int n) {
    {
        for (int i = 0; i < n-1; i++){
            a[i+1] = b[i]+c[i];
            b[i]   = c[i]*e[i];
            d[i]   = a[i]*e[i];
        }
    }
}
