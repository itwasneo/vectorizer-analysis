/* TSVC integer adaptation: s31111 (one computational repetition).
 * Contract: 32 <= n <= 1073741823; no SIMD-width divisibility requirement.
 * Arrays: a: read. Each has at least max(1,n) initialized ints.
 * Distinct array arguments occupy non-overlapping storage. No restrict added.
 * Every signed intermediate must fit in int; no wraparound assumption.
 * See ../contracts/s31111.json for the complete contract and adaptations.
 * Source SHA256: b89d270d9be22972a3c1d9b310c9c290a596aafb5c329ba5812afafadf41bedb
 */
#include <limits.h>
_Static_assert(INT_MAX == 2147483647, "This dataset requires 32-bit int");

static int tsvc_test(const int *A) {
  int s = (int)0;
                  
  for (int i = 0; i < 4; i++)
    s += A[i];
  return s;
}

int s31111(const int *a, int n) {
    (void)n;
    int sum;
    {
        sum = (int)0;
        sum += tsvc_test(a);
        sum += tsvc_test(&a[4]);
        sum += tsvc_test(&a[8]);
        sum += tsvc_test(&a[12]);
        sum += tsvc_test(&a[16]);
        sum += tsvc_test(&a[20]);
        sum += tsvc_test(&a[24]);
        sum += tsvc_test(&a[28]);
    }
    return sum;
}
