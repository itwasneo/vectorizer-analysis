/* TSVC integer adaptation: s342 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s342.json for the complete contract and adaptations.
 * Source SHA256: 1cea8bcf5f480a22c4f472e7822c7a2c49bb4f1555a50a175bc8c201a2f6f40b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s342(int *a, const int *b, int n) {
    int j = 0;
    {
        j = -1;
        for (int i = 0; i < n; i++) {
            if (a[i] > (int)0) {
                j++;
                a[i] = b[j];
            }
        }
    }
}
