/* TSVC integer adaptation: s341 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s341.json for the complete contract and adaptations.
 * Source SHA256: 4448e3c41ceba0ade1def60b9cef5c361fec1bd73aa9673f6d36302e392f6d96
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s341(int *a, const int *b, int n) {
    int j;
    {
        j = -1;
        for (int i = 0; i < n; i++) {
            if (b[i] > (int)0) {
                j++;
                a[j] = b[i];
            }
        }
    }
}
