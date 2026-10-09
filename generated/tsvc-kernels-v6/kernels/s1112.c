/* TSVC integer adaptation: s1112 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1112.json for the complete contract and adaptations.
 * Source SHA256: f7919cdb3652ea23fbb533c0c2b880e099d4ed4a9d709d7dcbae85cacd7493fb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1112(int *a, const int *b, int n) {
    {
        for (int i = n - 1; i >= 0; i--) {
            a[i] = b[i] + (int) 1;
        }
    }
}
