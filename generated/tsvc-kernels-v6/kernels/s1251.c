/* TSVC integer adaptation: s1251 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read_write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1251.json for the complete contract and adaptations.
 * Source SHA256: 805126f9a2902af3f699d9c6413b49d58b979d30a69ca8eed5ea9970f768da23
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1251(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    int s;
    {
        for (int i = 0; i < n; i++) {
            s = b[i]+c[i];
            b[i] = a[i]+d[i];
            a[i] = s*e[i];
        }
    }
}
