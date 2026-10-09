/* TSVC integer adaptation: s1111 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1111.json for the complete contract and adaptations.
 * Source SHA256: b0a6656ea5bda4036262755f7f714d040c273f7919bc9dd94e4d74862e04eae9
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1111(int *a, const int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n/2; i++) {
            a[2*i] = c[i] * b[i] + d[i] * b[i] + c[i] * c[i] + d[i] * b[i] + d[i] * c[i];
        }
    }
}
