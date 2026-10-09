/* TSVC integer adaptation: s274 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s274.json for the complete contract and adaptations.
 * Source SHA256: 4901d2a40efdc5aed7b69f8d1223223fb3730e52f8dfb0122324f98b557d5943
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s274(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = c[i] + e[i] * d[i];
            if (a[i] > (int)0) {
                b[i] = a[i] + b[i];
            } else {
                a[i] = d[i] * e[i];
            }
        }
    }
}
