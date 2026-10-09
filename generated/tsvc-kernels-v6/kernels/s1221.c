/* TSVC integer adaptation: s1221 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read_write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1221.json for the complete contract and adaptations.
 * Source SHA256: 3e4d8c35805c82d5f926aaa489f6b8d8816c852771f88b9543dd6f6845e12ea8
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1221(const int *a, int *b, int n) {
    {
        for (int i = 4; i < n; i++) {
            b[i] = b[i - 4] + a[i];
        }
    }
}
