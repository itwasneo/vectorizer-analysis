/* TSVC integer adaptation: s4113 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4113.json for the complete contract and adaptations.
 * Source SHA256: e108facd323d8104a263a2ae23cef5591eb4679ff14e324cc0a661c6f677791c
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s4113(int *a, const int *b, const int *c, const int *ip, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[ip[i]] = b[ip[i]] + c[i];
        }
    }
}
