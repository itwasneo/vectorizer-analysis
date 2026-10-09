/* TEST ONLY: original s261 with its harness disabled, not the extracted kernel.
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
static int *a;
static const int *b;
static int *c;
static const int *d;

int original_s261()
{

//	scalar and array expansion
//	wrap-around scalar under an if

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s261 ");
	start_t = clock();

	TYPE t;
	for (int nl = 0; nl < 1; nl++) {
		for (int i = 1; i < LEN; ++i) {
			t = a[i] + b[i];
			a[i] = t + c[i-1];
			t = c[i] * d[i];
			c[i] = t;
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S261\t %.2f \t\t", clock_dif_sec);;
	check(25);
	return 0;
}

void reference_s261(int *arg_a, const int *arg_b, int *arg_c, const int *arg_d, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    b = arg_b;
    c = arg_c;
    d = arg_d;
    original_s261();
}
