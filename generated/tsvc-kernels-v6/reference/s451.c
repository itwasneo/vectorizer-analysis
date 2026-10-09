/* TEST ONLY: original s451 with its harness disabled, not the extracted kernel.
 * Retains the original global names, declarations, computational statements and
 * epilogue. LEN/LEN2 are bound at runtime; nl executes exactly once.
 * Do not send this file to the LLM or use it for performance measurement.
 */
#include <time.h>
#include <math.h>
#undef USE_FLOAT_TRIG
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
static int *a;
static const int *b;
static const int *c;

int original_s451()
{

//	intrinsic functions
//	intrinsics

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s451 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN; i++) {
#ifdef USE_FLOAT_TRIG
			a[i] = sinf(b[i]) + cosf(c[i]);
#else
			a[i] = sin(b[i]) + cos(c[i]);
#endif
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S451\t %.2f \t\t", clock_dif_sec);;
	check(1);
	return 0;
}

void reference_s451(int *arg_a, const int *arg_b, const int *arg_c, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    b = arg_b;
    c = arg_c;
    original_s451();
}
