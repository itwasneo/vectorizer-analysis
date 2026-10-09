/* TSVC integer adaptation: s481 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, d: read. Each has at least max(1,n) initialized ints.
 * Return first negative d index before its update, or -1 on completion; never terminate the process.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s481.json for the complete contract and adaptations.
 * Source SHA256: 9eb5110a692984cf5541dacf0e216d12eeef050c1cec0228b54f7c4948986eab
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s481(int *a, const int *b, const int *c, const int *d, int n) {
    {
        for (int i = 0; i < n; i++) {
            if (d[i] < (int)0) {
                return i;
            }
            a[i] += b[i] * c[i];
        }
    }
    return -1;
}
