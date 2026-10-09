/* TSVC integer adaptation: s212 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s212.json for the complete contract and adaptations.
 * Source SHA256: 2c208c2f443ccbd47bec413564cb864291444e4230628201e0a882a93c516ebc
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s212(int *a, int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n-1; i++) {
            a[i] *= c[i];
            b[i] += a[i + 1] * d[i];
        }
    }
}
