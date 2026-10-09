/* TSVC integer adaptation: s2251 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s2251.json for the complete contract and adaptations.
 * Source SHA256: 3fdfe5716239c410ca408ee160c33665e995f1106f3c0d04c02c6f0060d64b87
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s2251(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        int s = (int)0;
        for (int i = 0; i < n; i++) {
            a[i] = s*e[i];
            s = b[i]+c[i];
            b[i] = a[i]+d[i];
        }
    }
}
