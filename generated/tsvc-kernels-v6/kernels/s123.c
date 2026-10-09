/* TSVC integer adaptation: s123 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s123.json for the complete contract and adaptations.
 * Source SHA256: 4b71e20e4b4917cbec7b63576fcaf24a7f5e45f8d91c403f77514a15802f39b1
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s123(int *a, const int *b, const int *c, const int *d, const int *e, int n) {
    int j;
    {
        j = -1;
        for (int i = 0; i < (n/2); i++) {
            j++;
            a[j] = b[i] + d[i] * e[i];
            if (c[i] > (int)0) {
                j++;
                a[j] = c[i] + d[i] * e[i];
            }
        }
    }
}
