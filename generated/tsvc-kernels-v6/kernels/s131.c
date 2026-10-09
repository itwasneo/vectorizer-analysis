/* TSVC integer adaptation: s131 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s131.json for the complete contract and adaptations.
 * Source SHA256: a2bbe31de08227f23d6aa9e660403c8d3abae2af7e10e9f3c8cdc68644ea2274
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s131(int *a, const int *b, int n) {
    int m  = 1;
    {
        for (int i = 0; i < n - 1; i++) {
            a[i] = a[i + m] + b[i];
        }
    }
}
