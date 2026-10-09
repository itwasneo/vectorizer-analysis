/* TEST ONLY: original s258 with its harness disabled, not the extracted kernel.
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
static const int *reference_storage_aa;
static int *b;
static const int *c;
static const int *d;
static int *e;

int original_s258(int reference_ld) {
    const int (*aa)[reference_ld] = (const int (*)[reference_ld])reference_storage_aa;

//	scalar and array expansion
//	wrap-around scalar under an if

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s258 ");
	start_t = clock();

	TYPE s;
	for (int nl = 0; nl < 1; nl++) {
		s = 0.;
		for (int i = 0; i < LEN; ++i) {
			if (a[i] > 0.) {
				s = d[i] * d[i];
			}
			b[i] = s * c[i] + d[i];
			e[i] = (s + (TYPE)1.) * aa[0][i];
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S258\t %.2f \t\t", clock_dif_sec);;
	check(25);
	return 0;
}

void reference_s258(const int *arg_a, const int *arg_aa, int *arg_b, const int *arg_c, const int *arg_d, int *arg_e, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_aa = arg_aa;
    b = arg_b;
    c = arg_c;
    d = arg_d;
    e = arg_e;
    original_s258(arg_ld);
}
