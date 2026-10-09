/* TSVC integer adaptation: s152 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: write, c: read, d: read, e: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s152.json for the complete contract and adaptations.
 * Source SHA256: 3c8507557a53625cc8fa7b5a3aa6c7450eedc8ebfad06a3a7015e47c49c21f7e
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_s152s(int *a, const int *b, const int *c, int i) {
	a[i] += b[i] * c[i];
	return 0;
}

void s152(int *a, int *b, const int *c, const int *d, const int *e, int n) {
    {
        for (int i = 0; i < n; i++) {
            b[i] = d[i] * e[i];
            tsvc_s152s(a, b, c, i);
        }
    }
}
