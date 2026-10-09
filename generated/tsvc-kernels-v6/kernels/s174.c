/* TSVC integer adaptation: s174 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Scalar contract: 0 <= M <= n/2.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s174.json for the complete contract and adaptations.
 * Source SHA256: fb3c97f536a1d928d6900e75eacfb8423cc2125063be59203273023b871bead8
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s174(int *a, const int *b, int M, int n) {
    (void)n;
    {
        for (int i = 0; i < M; i++) {
            a[i+M] = a[i] + b[i];
        }
    }
}
