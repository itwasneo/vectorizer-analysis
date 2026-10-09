/* TSVC integer adaptation: s331 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Scalar output pointers each address one initialized int, disjoint from all other buffers.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s331.json for the complete contract and adaptations.
 * Source SHA256: 1be3621cb2c42756e2bd57e5b8bb158356d48f1a29f45d5f9839ddf386999984
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s331(const int *a, int *out_j, int *out_chksum, int n) {
    int j;
    int chksum;
    {
        j = -1;
        for (int i = 0; i < n; i++) {
            if (a[i] < (int)0) {
                j = i;
            }
        }
        chksum = (int) j;
    }
    *out_j = j;
    *out_chksum = chksum;
    return j+1;
}
