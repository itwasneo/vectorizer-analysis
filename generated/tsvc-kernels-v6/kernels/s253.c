/* TSVC integer adaptation: s253 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read_write, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s253.json for the complete contract and adaptations.
 * Source SHA256: f9f869a86fa31d5c87db9924f610ef559a5dc5748110cbd0bee72b7f3f80eb68
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s253(int *a, const int *b, int *c, const int *d, int n) {
    int s;
    {
        for (int i = 0; i < n; i++) {
            if (a[i] > b[i]) {
                s = a[i] - b[i] * d[i];
                c[i] += s;
                a[i] = s;
            }
        }
    }
}
