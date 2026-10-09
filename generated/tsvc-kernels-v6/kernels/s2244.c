/* TSVC integer adaptation: s2244 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2244.json for the complete contract and adaptations.
 * Source SHA256: 0f0a3de0e4590a5ab7be5d7f37d9f90a9c5324501c6b8a88274a23e8d0597ed0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s2244(int *a, const int *b, const int *c, const int *e, int n) {
    {
        for (int i = 0; i < n-1; i++) {
            a[i+1] = b[i] + e[i];
            a[i] = b[i] + c[i];
        }
    }
}
