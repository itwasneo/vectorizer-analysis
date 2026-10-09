/* TEST ONLY: original s256 with its harness disabled, not the extracted kernel.
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
static const int *reference_storage_bb;
static int *reference_storage_cc;
static const int *d;

int original_s256(int reference_ld) {
    const int (*bb)[reference_ld] = (const int (*)[reference_ld])reference_storage_bb;
    int (*cc)[reference_ld] = (int (*)[reference_ld])reference_storage_cc;

//	scalar and array expansion
//	array expansion

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s256 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 0; i < LEN2; i++) {
			for (int j = 1; j < LEN2; j++) {
				a[j] = (TYPE)1.0 - a[j - 1];
				cc[j][i] = a[j] + bb[j][i]*d[j];
			}
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S256\t %.2f \t\t", clock_dif_sec);;
	check(111);
	return 0;
}

void reference_s256(int *arg_a, const int *arg_bb, int *arg_cc, const int *arg_d, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_bb = arg_bb;
    reference_storage_cc = arg_cc;
    d = arg_d;
    original_s256(arg_ld);
}
