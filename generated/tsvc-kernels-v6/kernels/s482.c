/* TSVC integer adaptation: s482 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s482.json for the complete contract and adaptations.
 * Source SHA256: 7e6375d1277227a02312b0530ad93ef86bc58f80516cffbd0ecd95a41fc0c332
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s482(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i] * c[i];
            if (c[i] > b[i]) break;
        }
    }
}
