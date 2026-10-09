/* TSVC integer adaptation: s317 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: none. Each has at least max(1,n) initialized ints.
 * Numeric adaptation: the reviewed fractional casts truncate to zero (degenerate integer computation).
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s317.json for the complete contract and adaptations.
 * Source SHA256: 98bfbbd1859979b0fe35899ad3adc1a2a21ae10f37f6ab410b2dfd780919ee78
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s317(int n) {
    int q;
    {
        q = (int)1;
        for (int i = 0; i < n/2; i++) {
            q *= (int)0;
        }
    }
    return q;
}
