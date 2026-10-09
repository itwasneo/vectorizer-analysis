/* TSVC integer adaptation: s315 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Scalar output pointers each address one initialized int, disjoint from all other buffers.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s315.json for the complete contract and adaptations.
 * Source SHA256: 68bce7ed696a18f80c12de6e79a27b3e561336ab0d69428d2b783fffc6ccec90
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s315(const int *a, int *out_x, int *out_index, int *out_chksum, int n) {
    int x, chksum;
    int index;
    {
        x = a[0];
        index = 0;
        for (int i = 0; i < n; ++i) {
            if (a[i] > x) {
                x = a[i];
                index = i;
            }
        }
        chksum = x + (int) index;
    }
    *out_x = x;
    *out_index = index;
    *out_chksum = chksum;
    return index+x+1;
}
