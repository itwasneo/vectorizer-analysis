/* TSVC integer adaptation: s4121 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4121.json for the complete contract and adaptations.
 * Source SHA256: 0e4e5596ac450d60d473a2fdf4b56d78127948ed1a141e16ada00b1d90adc8b7
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_f(int a, int b) {
	return a*b;
}

void s4121(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += tsvc_f(b[i], c[i]);
        }
    }
}
