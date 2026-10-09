/* TSVC integer adaptation: s318 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * a instead requires max(1, n*inc) initialized ints; allocation bytes must fit SIZE_MAX.
 * Scalar contract: 0 <= inc <= INT_MAX/max(1,n).
 * Scalar output pointers each address one initialized int, disjoint from all other buffers.
 * No element of a may equal INT_MIN (integer absolute-value contract).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s318.json for the complete contract and adaptations.
 * Source SHA256: 4e3e30089d504ac8493832c84fb6f8583902bca07a525573c45907b6d76c9c76
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_abs(int value) { return value < 0 ? -value : value; }

int s318(const int *a, int *out_max, int *out_index, int *out_chksum, int inc, int n) {
    int k, index;
    int max, chksum;
    {
        k = 0;
                index = 0;
                max = tsvc_abs(a[0]);
                k += inc;
                for (int i = 1; i < n; i++) {
                    if (tsvc_abs(a[k]) <= max) {
                        goto L5;
                    }
                    index = i;
                    max = tsvc_abs(a[k]);
        L5:
                    k += inc;
                }
                chksum = max + (int) index;
    }
    *out_max = max;
    *out_index = index;
    *out_chksum = chksum;
    return max + index+1;
}
