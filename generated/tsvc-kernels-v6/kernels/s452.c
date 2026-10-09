/* TSVC integer adaptation: s452 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s452.json for the complete contract and adaptations.
 * Source SHA256: 498a84524bb67deb2964e5e383d42b745072ce499f3be10b9d846fddddee729c
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s452(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = b[i] + c[i] * (int) (i+1);
        }
    }
}
