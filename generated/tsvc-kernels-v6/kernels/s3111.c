/* TSVC integer adaptation: s3111 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s3111.json for the complete contract and adaptations.
 * Source SHA256: 75cfb0acf472482253acacc21c140b8726a306701d709bbad0110c6c2500511a
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s3111(const int *a, int n) {
    int sum;
    {
        sum = 0;
        for (int i = 0; i < n; i++) {
            if (a[i] > (int)0) {
                sum += a[i];
            }
        }
    }
    return sum;
}
