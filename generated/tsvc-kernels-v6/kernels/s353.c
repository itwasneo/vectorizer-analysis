/* TSVC integer adaptation: s353 (one computational repetition).
 * Contract: 0 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read_write, b: read, c: read, ip: read. Each has at least max(1,n) initialized ints.
 * n must be divisible by 5, as required by the original unrolled loop.
 * For 0 <= i < n: 0 <= ip[i] < n. Duplicates are allowed; preserve store order.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s353.json for the complete contract and adaptations.
 * Source SHA256: 9cf99b5736a55facceb6c3aa2f000444108006eebfbc27553ced0d505411ae77
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

void s353(int *a, const int *b, const int *c, const int *ip, int n) {
    int alpha = c[0];
    {
        for (int i = 0; i < n; i += 5) {
            a[i] += alpha * b[ip[i]];
            a[i + 1] += alpha * b[ip[i + 1]];
            a[i + 2] += alpha * b[ip[i + 2]];
            a[i + 3] += alpha * b[ip[i + 3]];
            a[i + 4] += alpha * b[ip[i + 4]];
        }
    }
}
