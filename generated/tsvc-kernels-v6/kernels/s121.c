/* TSVC integer adaptation: s121 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s121.json for the complete contract and adaptations.
 * Source SHA256: 63cb59152ab2c33f6c519bae5918d3e50f874ed689adc638b84102f70b50f843
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s121(int *a, const int *b, int n) {
    int j;
    {
        for (int i = 0; i < n-1; i++) {
            j = i + 1;
            a[i] = a[j] + b[i];
        }
    }
}
