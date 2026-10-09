/* TSVC integer adaptation: s319 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s319.json for the complete contract and adaptations.
 * Source SHA256: 1e0fd564929ed4803008b4913146da21816a6e3a08d389c4ab1487bdde8eb9ea
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s319(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    int sum;
    {
        sum = 0;
        for (int i = 0; i < n; i++) {
            a[i] = c[i] + d[i];
            sum += a[i];
            b[i] = c[i] + e[i];
            sum += b[i];
        }
    }
    return sum;
}
