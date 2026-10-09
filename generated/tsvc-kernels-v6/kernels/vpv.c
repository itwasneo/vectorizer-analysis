/* TSVC integer adaptation: vpv (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vpv.json for the complete contract and adaptations.
 * Source SHA256: 3d7789228d61677612dbf2f8312cf5b4500b8eb501fd2d29b06aee98a080a654
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vpv(int *a, const int *b, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i];
        }
    }
}
