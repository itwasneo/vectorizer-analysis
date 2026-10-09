/* TEST ONLY: original s471 with its harness disabled, not the extracted kernel.
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
static int *b;
static const int *c;
static const int *d;
static const int *e;
static int *x;

static int s471s(void) {
// --  dummy subroutine call made in s471
	return 0;
}

int original_s471(){

//	call statements

	int m = LEN;
	/* Initialization is supplied by the caller. */
	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s471 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < m; i++) {
			x[i] = b[i] + d[i] * d[i];
			s471s();
			b[i] = c[i] + d[i] * e[i];
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S471\t %.2f \t\t", clock_dif_sec);;
	temp = 0.;
	for (int i = 0; i < LEN; i++){
		temp += x[i];
	}
	check(-12);
	return 0;
}

int reference_s471(int *arg_b, const int *arg_c, const int *arg_d, const int *arg_e, int *arg_x, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    b = arg_b;
    c = arg_c;
    d = arg_d;
    e = arg_e;
    x = arg_x;
    original_s471();
    return temp;
}
