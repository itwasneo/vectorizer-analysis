/* TSVC integer adaptation: s1213 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1213.json for the complete contract and adaptations.
 * Source SHA256: e43ad71048d1cc52a5eb6bf09923338d741eadbc81eaed40b054ea56ee484c47
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1213(int *a, int *b, const int *c, const int *d, int n) {
    {
        for (int i = 1; i < n-1; i++) {
            a[i] = b[i-1]+c[i];
            b[i] = a[i+1]*d[i];
        }
    }
}
