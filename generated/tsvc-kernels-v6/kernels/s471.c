/* TSVC integer adaptation: s471 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: b: read_write, c: read, d: read, e: read, x: write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s471.json for the complete contract and adaptations.
 * Source SHA256: a184e93e7bcf9f848c306f31e487a1d0b468e373f9f8ecb08c8ab5abfb4c0871
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_s471s(void) {
                                         
	return 0;
}

int s471(int *b, const int *c, const int *d, const int *e, int *x, int n) {
    int checksum;
    int m = n;
    {
        for (int i = 0; i < m; i++) {
            x[i] = b[i] + d[i] * d[i];
            tsvc_s471s();
            b[i] = c[i] + d[i] * e[i];
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++){
            checksum += x[i];
        }
    return checksum;
}
