/* TSVC integer adaptation: s172 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Scalar contract: 1 <= n1 <= n+1.
 * Scalar contract: 1 <= n3 <= INT_MAX-n.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s172.json for the complete contract and adaptations.
 * Source SHA256: 0c09a32972ce2577ff3f0bae6ace23c035ab7c6cdabe2b095e7b07531c5efb50
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s172(int *a, const int *b, int n1, int n3, int n) {
    {
        for (int i = n1-1; i < n; i += n3) {
            a[i] += b[i];
        }
    }
}
