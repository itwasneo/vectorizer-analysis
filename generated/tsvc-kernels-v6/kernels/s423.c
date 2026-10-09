/* TSVC integer adaptation: s423 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, array: read_write. Each has at least max(1,n) initialized ints.
 * array instead requires max(1, n+64) initialized ints; allocation bytes must fit SIZE_MAX.
 * xx initially aliases array+(64) ints; not an independent buffer.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s423.json for the complete contract and adaptations.
 * Source SHA256: 951267e5a117ad41d5137c9684e7525e90dba134a3c8baa8c0169950507f8432
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s423(const int *a, int *array, int n) {
    const int *xx;
    int checksum;
    int vl = 64;
    xx = array+vl;
    {
        for (int i = 0; i < n - 1; i++) {
            array[i+1] = xx[i] + a[i];
        }
    }
    checksum = 0;
        for (int i = 0; i < n; i++){
            checksum += array[i];
        }
    return checksum;
}
