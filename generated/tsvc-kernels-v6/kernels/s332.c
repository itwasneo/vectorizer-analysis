/* TSVC integer adaptation: s332 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Scalar output pointers each address one initialized int, disjoint from all other buffers.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s332.json for the complete contract and adaptations.
 * Source SHA256: 5adc16dcd31e58f97988238ab02b707915949864b7f3c2cac57ae4ff4c0d976b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s332(const int *a, int *out_index, int *out_chksum, int t, int n) {
    int index;
    int value;
    int chksum;
    {
        index = -2;
                value = -1;
                for (int i = 0; i < n; i++) {
                    if (a[i] > t) {
                        index = i;
                        value = a[i];
                        goto L20;
                    }
                }
        L20:
                chksum = value + (int) index;
    }
    *out_index = index;
    *out_chksum = chksum;
    return value;
}
