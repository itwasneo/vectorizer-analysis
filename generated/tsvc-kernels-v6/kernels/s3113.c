/* TSVC integer adaptation: s3113 (one computational repetition).
 * Contract: 1 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * No element of a may equal INT_MIN (integer absolute-value contract).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s3113.json for the complete contract and adaptations.
 * Source SHA256: 0d854b0d4db502371497618326b27f7867e5359e4e6a9ff614bff71bb2ff0a9f
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_abs(int value) { return value < 0 ? -value : value; }

int s3113(const int *a, int n) {
    int max;
    {
        max = tsvc_abs(a[0]);
        for (int i = 0; i < n; i++) {
            if ((tsvc_abs(a[i])) > max) {
                max = tsvc_abs(a[i]);
            }
        }
    }
    return max;
}
