/* TSVC integer adaptation: s128 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s128.json for the complete contract and adaptations.
 * Source SHA256: b15ed0b2b3e36beee8f1e58f53611c1eb11a37b3ead709e4a153e10df91876fb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s128(int *a, int *b, const int *c, const int *d, int n) {
    int j, k;
    {
        j = -1;
        for (int i = 0; i < n/2; i++) {
            k = j + 1;
            a[i] = b[k] - d[i];
            j = k + 1;
            b[k] = a[i] + c[k];
        }
    }
}
