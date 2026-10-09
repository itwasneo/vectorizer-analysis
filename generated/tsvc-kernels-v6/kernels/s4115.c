/* TSVC integer adaptation: s4115 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read, ip: read. Each has at least max(1,n) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4115.json for the complete contract and adaptations.
 * Source SHA256: b8fdbdb8fedf23080b9f1bdd72ffe6bb256d1b1698c3a064691dd64a98f20b14
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s4115(const int *a, const int *b, const int *ip, int n) {
    int sum;
    {
        sum = 0;
        for (int i = 0; i < n; i++) {
            sum += a[i] * b[ip[i]];
        }
    }
    return sum;
}
