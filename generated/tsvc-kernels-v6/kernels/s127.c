/* TSVC integer adaptation: s127 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s127.json for the complete contract and adaptations.
 * Source SHA256: dc6bcdd822ab5d9b234a8bcacc58a2f4d32666c43218ad4fba04f22ebd6da8a2
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s127(int *a, const int *b, const int *c, const int *d, const int *e, int n) {
    int j;
    {
        j = -1;
        for (int i = 0; i < n/2; i++) {
            j++;
            a[j] = b[i] + c[i] * d[i];
            j++;
            a[j] = b[i] + d[i] * e[i];
        }
    }
}
