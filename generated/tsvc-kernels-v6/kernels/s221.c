/* TSVC integer adaptation: s221 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s221.json for the complete contract and adaptations.
 * Source SHA256: 293cacdad1b77d299820f48ae25cdce29a2415494a2cf8427bb38bd7663d691f
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s221(int *a, int *b, const int *c, const int *d, int n) {
    {
        for (int i = 1; i < n; i++) {
            a[i] += c[i] * d[i];
            b[i] = b[i - 1] + a[i] + d[i];
        }
    }
}
