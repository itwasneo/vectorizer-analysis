/* TSVC integer adaptation: s124 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s124.json for the complete contract and adaptations.
 * Source SHA256: 1dffb3ac4e0cb6ffb5d1e34f2c48b788bf432859829eab8a4e38e8801a1cea99
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s124(int *a, const int *b, const int *c, const int *d, const int *e, int n) {
    int j;
    {
        j = -1;
        for (int i = 0; i < n; i++) {
            if (b[i] > (int)0) {
                j++;
                a[j] = b[i] + d[i] * e[i];
            } else {
                j++;
                a[j] = c[i] + d[i] * e[i];
            }
        }
    }
}
