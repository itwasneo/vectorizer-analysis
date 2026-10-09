/* TEST ONLY: original s4116 with its harness disabled, not the extracted kernel.
 * Retains the original global names, declarations, computational statements and
 * epilogue. LEN/LEN2 are bound at runtime; nl executes exactly once.
 * Do not send this file to the LLM or use it for performance measurement.
 */
#include <time.h>
#define TYPE int
#define LEN reference_n
#define lll LEN
#define LEN2 reference_n
#define clock() ((clock_t)0)
#define init(...) ((void)0)
#define check(...) ((void)0)
#define printf(...) ((void)0)
#define dummy(a,b,c,d,e,aa,bb,cc,value) (reference_last_scalar = (value))
static int reference_n;
static int reference_last_scalar;
static int temp;
static const int *a;
static const int *reference_storage_aa;

int original_s4116(int* __restrict__ ip, int j, int inc, int reference_ld) {
    const int (*aa)[reference_ld] = (const int (*)[reference_ld])reference_storage_aa;

//	indirect addressing
//	more complicated sparse sdot
//	gather is required

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s4116");
	start_t = clock();

	TYPE sum;
	int off;
	for (int nl = 0; nl < 1; nl++) {
		sum = 0.;
		for (int i = 0; i < LEN2-1; i++) {
			off = inc + i;
			sum += a[off] * aa[j-1][ip[i]];
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S4116\t %.2f \t\t", clock_dif_sec);;
	temp = sum;
	check(-1);
	return 0;
}

int reference_s4116(const int *arg_a, const int *arg_aa, const int *arg_ip, int arg_j, int arg_inc, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_aa = arg_aa;
    original_s4116((int *)arg_ip, arg_j, arg_inc, arg_ld);
    return temp;
}
