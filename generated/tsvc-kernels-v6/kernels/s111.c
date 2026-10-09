/* TSVC integer adaptation: s111 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s111.json for the complete contract and adaptations.
 * Source SHA256: e8adddb2e4a1d9b403bb8271fffede543ef242f7a708051965ded31535f0f31b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s111(int *a, const int *b, int n) {
    {
        for (int i = 1; i < n; i += 2) {
            a[i] = a[i - 1] + b[i];
        }
    }
}
