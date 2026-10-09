/* TSVC integer adaptation: vtvtv (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vtvtv.json for the complete contract and adaptations.
 * Source SHA256: 96c03cbd153c778a88665e9d7f6014401fc7dae43764e189414a1f4010e962a9
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vtvtv(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = a[i] * b[i] * c[i];
        }
    }
}
