/* TSVC integer adaptation: s4116 (one computational repetition).
 * Contract: 0 <= n <= 46340; no SIMD-width divisibility requirement.
 * Arrays: a: read, aa: read, ip: read. Square n*n matrices use ld >= max(1,n), with n*ld initialized ints (at least one).
 * Flat-square buffers use max(1,n*n) ints; vectors use max(1,n). Padding is preserved.
 * n*ld*sizeof(int) must fit in SIZE_MAX and the supplied allocation.
 * a instead requires max(1,n+inc) initialized ints.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Scalar contract: 1 <= j <= max(1,n).
 * Scalar contract: 0 <= inc <= INT_MAX-n.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s4116.json for the complete contract and adaptations.
 * Source SHA256: 64c6c1662ab1a4e5663c412ea0e6060a851f30d6bf051c83ad56c2c41b6830bc
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");
#include <stddef.h>

int s4116(const int *a, const int *aa, const int *ip, int j, int inc, int n, int ld) {
    int sum;
    int off;
    {
        sum = 0;
        for (int i = 0; i < n-1; i++) {
            off = inc + i;
            sum += a[off] * aa[(size_t)(j-1) * ld + (ip[i])];
        }
    }
    return sum;
}
