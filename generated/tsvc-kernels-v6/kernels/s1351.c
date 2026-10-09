/* TSVC integer adaptation: s1351 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * A initially aliases a+(0) ints; not an independent buffer.
 * B initially aliases b+(0) ints; not an independent buffer.
 * C initially aliases c+(0) ints; not an independent buffer.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s1351.json for the complete contract and adaptations.
 * Source SHA256: 998271d13c45160734498390b0fa02d5b4d869fe04b1d83d74b76d6d44a56218
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s1351(int *a, const int *b, const int *c, int n) {
    {
        int *A = a;
        const int *B = b;
        const int *C = c;
        for (int i = 0; i < n; i++) {
            *A = *B+*C;
            A++;
            B++;
            C++;
        }
    }
}
