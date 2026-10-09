/* TSVC integer adaptation: s431 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s431.json for the complete contract and adaptations.
 * Source SHA256: ccb539bd6c822b8034547c9328d54dd4ffb4f0a956285b48b717cf2dc1136f37
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s431(int *a, const int *b, int n) {
    int k1=1;
    int k2=2;
    int k=2*k1-k2;
    {
        for (int i = 0; i < n; i++) {
            a[i] = a[i+k] + b[i];
        }
    }
}
