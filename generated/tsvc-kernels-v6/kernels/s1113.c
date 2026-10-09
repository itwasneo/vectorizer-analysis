/* TSVC integer adaptation: s1113 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1113.json for the complete contract and adaptations.
 * Source SHA256: adc87afe04ed76d76579307c8e476564a1079477390e6d70a289dbd1a54db795
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1113(int *a, const int *b, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = a[n/2] + b[i];
        }
    }
}
