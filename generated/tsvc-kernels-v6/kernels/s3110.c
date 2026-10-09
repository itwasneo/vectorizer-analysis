/* TSVC integer adaptation: s3110 (one computational repetition).
 * Contract: 1 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: aa: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * Scalar output pointers each address one initialized int, disjoint from all other buffers.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s3110.json for the complete contract and adaptations.
 * Source SHA256: d6f4fb7bf61c1ff65a9435e6bbc1cdccfd9e1b59cda695d4317e2e54d9868b92
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

int s3110(const int *aa, int *out_max, int *out_xindex, int *out_yindex, int *out_chksum, int n, int ld) {
    int xindex, yindex;
    int max, chksum;
    {
        max = aa[(size_t)((0)) * ld + (0)];
        xindex = 0;
        yindex = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (aa[(size_t)(i) * ld + (j)] > max) {
                    max = aa[(size_t)(i) * ld + (j)];
                    xindex = i;
                    yindex = j;
                }
            }
        }
        chksum = max + (int) xindex + (int) yindex;
    }
    *out_max = max;
    *out_xindex = xindex;
    *out_yindex = yindex;
    *out_chksum = chksum;
    return max + xindex+1 + yindex+1;
}
