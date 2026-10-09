/* TSVC integer adaptation: s1281 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1281.json for the complete contract and adaptations.
 * Source SHA256: 18fb8e1a133c725f02c191ce3bda48ce5303f5e01b9ea2a9da93b282f41f05f0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1281(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    int x;
    {
        for (int i = 0; i < n; i++) {
            x = b[i]*c[i]+a[i]*d[i]+e[i];
            a[i] = x-(int)1;
            b[i] = x;
        }
    }
}
