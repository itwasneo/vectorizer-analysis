/* TEST ONLY: original s2275 with its harness disabled, not the extracted kernel.
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
static int *a;
static int *reference_storage_aa;
static const int *b;
static const int *reference_storage_bb;
static const int *c;
static const int *reference_storage_cc;
static const int *d;

int original_s2275(int reference_ld) {
    int (*aa)[reference_ld] = (int (*)[reference_ld])reference_storage_aa;
    const int (*bb)[reference_ld] = (const int (*)[reference_ld])reference_storage_bb;
    const int (*cc)[reference_ld] = (const int (*)[reference_ld])reference_storage_cc;

//	loop distribution is needed to be able to interchange

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s275 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN2; i++) {
			for (int j = 0; j < LEN2; j++) {
				aa[j][i] = aa[j][i] + bb[j][i] * cc[j][i];
			}
			a[i] = b[i] + c[i] * d[i];
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S2275\t %.2f \t\t", clock_dif_sec);;
	check(11);
	return 0;
}

void reference_s2275(int *arg_a, int *arg_aa, const int *arg_b, const int *arg_bb, const int *arg_c, const int *arg_cc, const int *arg_d, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_aa = arg_aa;
    b = arg_b;
    reference_storage_bb = arg_bb;
    c = arg_c;
    reference_storage_cc = arg_cc;
    d = arg_d;
    original_s2275(arg_ld);
}
