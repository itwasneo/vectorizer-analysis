/* TSVC integer adaptation: s4112 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4112.json for the complete contract and adaptations.
 * Source SHA256: 3e1cd17e897ff9f4f30e8d7df93b41699e3c83e6dbb1d380aeba86fd7889dab6
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s4112(int *a, const int *b, const int *ip, int s, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[ip[i]] * s;
        }
    }
}
