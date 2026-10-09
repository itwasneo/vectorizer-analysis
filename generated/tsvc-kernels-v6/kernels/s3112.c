/* TSVC integer adaptation: s3112 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: write. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s3112.json for the complete contract and adaptations.
 * Source SHA256: e832836924823c8c1c400af2f4b8ff9e3fb0a938e2db149cd96ae0c5bbba6b9e
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s3112(const int *a, int *b, int n) {
    int sum;
    {
        sum = (int)0;
        for (int i = 0; i < n; i++) {
            sum += a[i];
            b[i] = sum;
        }
    }
    return sum;
}
