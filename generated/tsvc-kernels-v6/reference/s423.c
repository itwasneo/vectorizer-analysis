/* TEST ONLY: original s423 with its harness disabled, not the extracted kernel.
 * Retains the original global names, declarations, computational statements and
 * epilogue. LEN/LEN2 are bound at runtime; nl executes exactly once.
 * Do not send this file to the LLM or use it for performance measurement.
 */
#include <time.h>
#define TYPE int
#define LEN reference_n
#define lll LEN
#define clock() ((clock_t)0)
#define init(...) ((void)0)
#define check(...) ((void)0)
#define printf(...) ((void)0)
#define dummy(a,b,c,d,e,aa,bb,cc,value) (reference_last_scalar = (value))
static int reference_n;
static int reference_last_scalar;
static int temp;
static const int *a;
static int *array;
static const int *xx;

int original_s423()
{

//	storage classes and equivalencing
//	common and equivalenced variables - with anti-dependence

	int vl = 64;
	xx = array+vl;
	/* Initialization is supplied by the caller. */
	clock_t start_t, end_t, clock_dif; double clock_dif_sec;
	init( "s423 ");
	start_t = clock();
	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN - 1; i++) {
			array[i+1] = xx[i] + a[i];
		}
		dummy(a, b, c, d, e, aa, bb, cc, 1.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S423\t %.2f \t\t", clock_dif_sec);;

	temp = 0.;
	for (int i = 0; i < LEN; i++){
		temp += array[i];
	}
	check(-1);
	return 0;
}

int reference_s423(const int *arg_a, int *arg_array, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    array = arg_array;
    original_s423();
    return temp;
}
