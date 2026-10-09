/* TSVC integer adaptation: s241 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s241.json for the complete contract and adaptations.
 * Source SHA256: 8ccd2dc4cdf98fa16333f25fa6fab087c7629eb8b8f64090b80df0b9be99825e
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s241(int *a, int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a[i+1] * d[i];
        }
    }
}
