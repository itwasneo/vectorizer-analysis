/* TSVC integer adaptation: s175 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * a instead requires max(1,n+inc) initialized ints.
 * Scalar contract: 1 <= inc <= INT_MAX-n.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s175.json for the complete contract and adaptations.
 * Source SHA256: 498b64d9ba91f5ab098900a909782cbfc002c7958a77e95cb38ff471b5ab88e6
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s175(int *a, const int *b, int inc, int n) {
    {
        for (int i = 0; i < n-1; i += inc) {
            a[i] = a[i + inc] + b[i];
        }
    }
}
