/* TSVC integer adaptation: s243 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s243.json for the complete contract and adaptations.
 * Source SHA256: 22ddf69dbb34ff6a166da0df56f1a4c3dc954dcf544d04ba3a92026efd8f06a3
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s243(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a[i+1] * d[i];
        }
    }
}
