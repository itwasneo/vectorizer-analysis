/* TSVC integer adaptation: s113 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s113.json for the complete contract and adaptations.
 * Source SHA256: da9bf8e56686317edeaec3e01e116d3f38f7010fc06704eec1a6a180f57e4cca
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s113(int *a, const int *b, int n) {
    {
        for (int i = 1; i < n; i++) {
            a[i] = a[0] + b[i];
        }
    }
}
