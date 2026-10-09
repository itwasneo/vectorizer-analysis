/* TSVC integer adaptation: s313 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s313.json for the complete contract and adaptations.
 * Source SHA256: f848a8d8cc6f9bc3bcbdf4c2586065703f3596ca94fac8a19ea4cfa47ed8dabf
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s313(const int *a, const int *b, int n) {
    int dot;
    {
        dot = (int)0;
        for (int i = 0; i < n; i++) {
            dot += a[i] * b[i];
        }
    }
    return dot;
}
