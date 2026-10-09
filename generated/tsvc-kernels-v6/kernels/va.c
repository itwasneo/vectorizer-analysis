/* TSVC integer adaptation: va (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/va.json for the complete contract and adaptations.
 * Source SHA256: da538f7311436038b91e9e73d156d25839faf99ced8c107d93406288426508bb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void va(int *a, const int *b, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] = b[i];
        }
    }
}
