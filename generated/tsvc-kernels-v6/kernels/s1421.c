/* TSVC integer adaptation: s1421 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read_write. Each has at least max(1,n) initialized ints.
 * xx initially aliases b+(n/2) ints; not an independent buffer.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1421.json for the complete contract and adaptations.
 * Source SHA256: 507872649366ee67686c8f5c637a44de23f190b818f76491cfa47f4282b63525
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s1421(const int *a, int *b, int n) {
    const int *xx;
    int checksum;
    xx = &b[n/2];
    {
        for (int i = 0; i < n/2; i++) {
            b[i] = xx[i] + a[i];
        }
    }
    checksum = 0;
        for (int i = 0; i < n/2; i++){
            checksum += xx[i];
        }
    return checksum;
}
