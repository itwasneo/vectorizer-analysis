/* TSVC integer adaptation: s281 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s281.json for the complete contract and adaptations.
 * Source SHA256: b83e8bcf7994c0f78f288a80a4e82a3ec6e474517ab6fbc7e30fef4b6b5ff008
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s281(int *a, int *b, const int *c, int n) {
    int x;
    {
        for (int i = 0; i < n; i++) {
            x = a[n-i-1] + b[i] * c[i];
            a[i] = x-(int)1;
            b[i] = x;
        }
    }
}
