/* TSVC integer adaptation: s122 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Scalar contract: 1 <= n1 <= n+1.
 * Scalar contract: 1 <= n3 <= INT_MAX-n.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s122.json for the complete contract and adaptations.
 * Source SHA256: a30f179bd411505864d548d7b9d1fd668c2e128535ece6dd52d16b81f3a3ff1d
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s122(int *a, const int *b, int n1, int n3, int n) {
    int j, k;
    {
        j = 1;
        k = 0;
        for (int i = n1-1; i < n; i += n3) {
            k += j;
            a[i] += b[n - k];
        }
    }
}
