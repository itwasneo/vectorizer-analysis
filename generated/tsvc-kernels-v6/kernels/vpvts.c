/* TSVC integer adaptation: vpvts (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vpvts.json for the complete contract and adaptations.
 * Source SHA256: 422392351b89992aad784238b482b860942b353f1e1ee16349172004b81db0e0
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void vpvts(int *a, const int *b, int s, int n) {
    {
        for (int i = 0; i < n; i++) {
            a[i] += b[i] * s;
        }
    }
}
