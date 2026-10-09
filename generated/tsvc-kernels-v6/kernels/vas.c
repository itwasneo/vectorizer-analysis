/* TSVC integer adaptation: vas (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vas.json for the complete contract and adaptations.
 * Source SHA256: 9543ac6d97969ecefee87ef99bb2e8ada59cebb612e0f6f8fe045d8c51faec36
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vas(int *a, const int *b, const int *ip, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[ip[i]] = b[i];
        }
    }
}
