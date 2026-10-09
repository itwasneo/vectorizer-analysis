/* TSVC integer adaptation: s171 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * a instead requires max(1, n*inc) initialized ints; allocation bytes must fit SIZE_MAX.
 * Scalar contract: 0 <= inc <= INT_MAX/max(1,n).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s171.json for the complete contract and adaptations.
 * Source SHA256: d1a8734b3fb311f69b72872a054c5ea9d740f2069c6099cb68f6ba518a896f52
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s171(int *a, const int *b, int inc, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i * inc] += b[i];
        }
    }
}
