/* TSVC integer adaptation: s453 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s453.json for the complete contract and adaptations.
 * Source SHA256: 1bcc54f6486837d86aee82a12c00e3083597afa224d650a84cec5a671b105bc8
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s453(int *a, const int *b, int n) {
    int s;
    {
        s = 0;
        for (int i = 0; i < n; i++) {
            s += (int)2;
            a[i] = s * b[i];
        }
    }
}
