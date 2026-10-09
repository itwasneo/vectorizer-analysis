/* TSVC integer adaptation: s252 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s252.json for the complete contract and adaptations.
 * Source SHA256: 81b2fc995fcfc9b55af338147197394397adae9cb79abab72a9d7f2fc15b5ead
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s252(int *a, const int *b, const int *c, int n) {
    int t, s;
    {
        t = (int) 0;
        for (int i = 0; i < n; i++) {
            s = b[i] * c[i];
            a[i] = s + t;
            t = s;
        }
    }
}
