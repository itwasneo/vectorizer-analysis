/* TSVC integer adaptation: s322 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s322.json for the complete contract and adaptations.
 * Source SHA256: 4e9f1209210d2f73ba422ad12014eb01bd60309ec5801ab493a786de45781aa4
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s322(int *a, const int *b, const int *c, int n) {
    {
        for (int i = 2; i < n; i++) {
            a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
    }
}
