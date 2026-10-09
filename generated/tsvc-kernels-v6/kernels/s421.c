/* TSVC integer adaptation: s421 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, xx: read_write. Each has at least max(1,n) initialized ints.
 * yy initially aliases xx+(0) ints; not an independent buffer.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s421.json for the complete contract and adaptations.
 * Source SHA256: 2c8bd89f062b65c5e2e811ab3d5d9c7f4af48802e406cfdc03b4b999009d71f0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s421(const int *a, int *xx, int n) {
    const int *yy;
    int checksum;
    {
        yy = xx;
        for (int i = 0; i < n - 1; i++) {
            xx[i] = yy[i+1] + a[i];
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++){
            checksum += xx[i];
        }
    return checksum;
}
