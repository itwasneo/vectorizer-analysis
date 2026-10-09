/* TSVC integer adaptation: s151 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s151.json for the complete contract and adaptations.
 * Source SHA256: 235f8ac94ebeb6749fe494594fadaf3720023764bdf8781c16ee19a1de040de0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_s151s(int *a, const int *b, int m, int n) {
	for (int i = 0; i < n-1; i++) {
		a[i] = a[i + m] + b[i];
	}
	return 0;
}

void s151(int *a, const int *b, int n) {
    {
        tsvc_s151s(a, b, 1, n);
    }
}
