/* TSVC integer adaptation: s352 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read, b: read. Each has at least max(1,n) initialized ints.
 * n must be divisible by 5, as required by the original unrolled loop.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s352.json for the complete contract and adaptations.
 * Source SHA256: 26317f91ed0f1fb704e54630a1b27bba1adb076befe4aee80833a3babc5f36d3
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

int s352(const int *a, const int *b, int n) {
    int dot;
    {
        dot = (int)0;
        for (int i = 0; i < n; i += 5) {
            dot = dot + a[i] * b[i] + a[i + 1] * b[i + 1] + a[i + 2]
                * b[i + 2] + a[i + 3] * b[i + 3] + a[i + 4] * b[i + 4];
        }
    }
    return dot;
}
