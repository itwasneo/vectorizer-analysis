/* TSVC integer adaptation: s424 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, array: read_write. Each has at least max(1,n) initialized ints.
 * array instead requires max(1, n+63) initialized ints; allocation bytes must fit SIZE_MAX.
 * xx initially aliases array+(63) ints; not an independent buffer.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s424.json for the complete contract and adaptations.
 * Source SHA256: 8deadcb08c49a2b25f4646e77b848862810e65288d7ce0c389c3d873d67d6e64
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s424(const int *a, int *array, int n) {
    int *xx;
    int checksum;
    int vl = 63;
    xx = array + vl;
    {
        for (int i = 0; i < n - 1; i++) {
            xx[i+1] = array[i] + a[i];
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++){
            checksum += xx[i];
        }
    return checksum;
}
