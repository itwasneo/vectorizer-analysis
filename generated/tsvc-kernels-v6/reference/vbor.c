/* TEST ONLY: original vbor with its harness disabled, not the extracted kernel.
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
static const int *b;
static const int *c;
static const int *d;
static const int *e;
static int *x;

int original_vbor(int reference_ld) {
    const int (*aa)[reference_ld] = (const int (*)[reference_ld])reference_storage_aa;

//	control loops
//	basic operations rates, isolate arithmetic from memory traffic
//	all combinations of three, 59 flops for 6 loads and 1 store.

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "vbor ");
	start_t = clock();

	TYPE a1, b1, c1, d1, e1, f1;
	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN; i++) {
			a1 = a[i];
			b1 = b[i];
			c1 = c[i];
			d1 = d[i];
			e1 = e[i];
			f1 = aa[0][i];
			a1 = a1 * b1 * c1 + a1 * b1 * d1 + a1 * b1 * e1 + a1 * b1 * f1 +
				a1 * c1 * d1 + a1 * c1 * e1 + a1 * c1 * f1 + a1 * d1 * e1
				+ a1 * d1 * f1 + a1 * e1 * f1;
			b1 = b1 * c1 * d1 + b1 * c1 * e1 + b1 * c1 * f1 + b1 * d1 * e1 +
				b1 * d1 * f1 + b1 * e1 * f1;
			c1 = c1 * d1 * e1 + c1 * d1 * f1 + c1 * e1 * f1;
			d1 = d1 * e1 * f1;
			x[i] = a1 * b1 * c1 * d1;
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("vbor\t %.2f \t\t", clock_dif_sec);;
	temp = 0.;
	for (int i = 0; i < LEN; i++){
		temp += x[i];
	}
	check(-1);
	return 0;
}

int reference_vbor(const int *arg_a, const int *arg_aa, const int *arg_b, const int *arg_c, const int *arg_d, const int *arg_e, int *arg_x, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_aa = arg_aa;
    b = arg_b;
    c = arg_c;
    d = arg_d;
    e = arg_e;
    x = arg_x;
    original_vbor(arg_ld);
    return temp;
}
