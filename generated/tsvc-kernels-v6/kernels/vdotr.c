/* TSVC integer adaptation: vdotr (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/vdotr.json for the complete contract and adaptations.
 * Source SHA256: b56929e1d1449caa9dae4196e198bf7bdb00e4c0f82d10fae30835cd0b64a41b
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int vdotr(const int *a, const int *b, int n) {
    int dot;
    {
        dot = 0;
        for (int i = 0; i < n; i++) {
            dot += a[i] * b[i];
        }
    }
    return dot;
}
