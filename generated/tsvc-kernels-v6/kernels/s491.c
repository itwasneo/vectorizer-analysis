/* TSVC integer adaptation: s491 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s491.json for the complete contract and adaptations.
 * Source SHA256: eabe0cb0140403474e589d68113c3e10ddeb7a484e3fc4f9f233185018382872
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s491(int *a, const int *b, const int *c, const int *d, const int *ip, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[ip[i]] = b[i] + c[i] * d[i];
        }
    }
}
