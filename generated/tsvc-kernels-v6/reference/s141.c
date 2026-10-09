/* TEST ONLY: original s141 with its harness disabled, not the extracted kernel.
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
static int *array;
static const int *reference_storage_bb;

int original_s141(int reference_ld) {
    const int (*bb)[reference_ld] = (const int (*)[reference_ld])reference_storage_bb;

//	nonlinear dependence testing
//	walk a row in a symmetric packed array
//	element a(i,j) for (int j>i) stored in location j*(j-1)/2+i

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s141 ");
	start_t = clock();

	int k;
	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN2; i++) {
			k = (i+1) * ((i+1) - 1) / 2 + (i+1)-1;
			for (int j = i; j < LEN2; j++) {
				array[k] += bb[j][i];
				k += j+1;
			}
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S141\t %.2f \t\t", clock_dif_sec);;
	check(0);
	return 0;
}

void reference_s141(int *arg_array, const int *arg_bb, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    array = arg_array;
    reference_storage_bb = arg_bb;
    original_s141(arg_ld);
}
