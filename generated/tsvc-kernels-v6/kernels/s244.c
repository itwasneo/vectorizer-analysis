/* TSVC integer adaptation: s244 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s244.json for the complete contract and adaptations.
 * Source SHA256: 37bf1ff1e9fc4df06d68a917e29fed5ef9643b301e79c23d05ff3ae3b763d904
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s244(int *a, int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a[i+1] = b[i] + a[i+1] * d[i];
        }
    }
}
