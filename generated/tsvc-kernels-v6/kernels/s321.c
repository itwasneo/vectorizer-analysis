/* TSVC integer adaptation: s321 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s321.json for the complete contract and adaptations.
 * Source SHA256: e3392111aaa0ff5faf0b458b58762c5c5618749e89bca6010deae49d61a95d2a
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s321(int *a, const int *b, int n) {
    {
        for (int i = 1; i < n; i++) {
            a[i] += a[i-1] * b[i];
        }
    }
}
