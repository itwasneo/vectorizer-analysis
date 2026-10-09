/* TEST ONLY: original s272 with its harness disabled, not the extracted kernel.
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
static int *b;
static const int *c;
static const int *d;
static const int *e;

int original_s272(TYPE t)
{

//	control flow
//	loop with independent conditional

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s272 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN; i++) {
			if (e[i] >= t) {
				a[i] += c[i] * d[i];
				b[i] += c[i] * c[i];
			}
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S272\t %.2f \t\t", clock_dif_sec);;
	check(12);
	return 0;
}

void reference_s272(int *arg_a, int *arg_b, const int *arg_c, const int *arg_d, const int *arg_e, int arg_t, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    b = arg_b;
    c = arg_c;
    d = arg_d;
    e = arg_e;
    original_s272(arg_t);
}
