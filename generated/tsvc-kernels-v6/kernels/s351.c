/* TSVC integer adaptation: s351 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read. Each has at least max(1,n) initialized ints.
 * n must be divisible by 5, as required by the original unrolled loop.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s351.json for the complete contract and adaptations.
 * Source SHA256: e3f24947875d9c503b89e869b2fb938cb396233c08401f0105f1693e8811ce64
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s351(int *a, const int *b, const int *c, int n) {
    int alpha = c[0];
    {
        for (int i = 0; i < n; i += 5) {
            a[i] += alpha * b[i];
            a[i + 1] += alpha * b[i + 1];
            a[i + 2] += alpha * b[i + 2];
            a[i + 3] += alpha * b[i + 3];
            a[i + 4] += alpha * b[i + 4];
        }
    }
}
