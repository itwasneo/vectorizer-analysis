/* TSVC integer adaptation: s173 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s173.json for the complete contract and adaptations.
 * Source SHA256: a2b939b8f684ef2ec54ec46f94a93fb440e6a6ff1ebd3feb1d14f724e45f88bb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s173(int *a, const int *b, int n) {
    int k = n/2;
    {
        for (int i = 0; i < n/2; i++) {
            a[i+k] = a[i] + b[i];
        }
    }
}
