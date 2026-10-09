/* TSVC integer adaptation: s4114 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, d: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Scalar contract: 1 <= n1 <= n+1.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4114.json for the complete contract and adaptations.
 * Source SHA256: 030fda6af62c1f3ec5ea418bdd126d00ee982b8da18a2ef6f1e76b4a81382a57
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s4114(int *a, const int *b, const int *c, const int *d, const int *ip, int n1, int n) {
    int k;
    {
        for (int i = n1-1; i < n; i++) {
            k = ip[i];
            a[i] = b[i] + c[n-k+1-2] * d[i];
            k += 5;
        }
    }
}
