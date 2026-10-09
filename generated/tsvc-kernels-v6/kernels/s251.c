/* TSVC integer adaptation: s251 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s251.json for the complete contract and adaptations.
 * Source SHA256: 0f7e7d7980b9281f43f24e74a456ac5e7366b9e4b00dfd0a5a58521708d3104e
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s251(int *a, const int *b, const int *c, const int *d, int n) {
    int s;
    {
        for (int i = 0; i < n; i++) {
            s = b[i] + c[i] * d[i];
            a[i] = s * s;
        }
    }
}
