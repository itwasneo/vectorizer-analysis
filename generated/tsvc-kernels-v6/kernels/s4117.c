/* TSVC integer adaptation: s4117 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4117.json for the complete contract and adaptations.
 * Source SHA256: 46b98fd1f9d9091b746eb28813daafcdee81ce25f2599b4e9e1f0c93a8c082b3
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s4117(int *a, const int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = b[i] + c[i/2] * d[i];
        }
    }
}
