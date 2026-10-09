/* TEST ONLY: original s118 with its harness disabled, not the extracted kernel.
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

int original_s118(int reference_ld) {
    const int (*bb)[reference_ld] = (const int (*)[reference_ld])reference_storage_bb;

//	linear dependence testing
//	potential dot product recursion

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s118 ");
	start_t = clock();

	for (int nl = 0; nl < 1; nl++) {
		for (int i = 1; i < LEN2; i++) {
			for (int j = 0; j <= i - 1; j++) {
				a[i] += bb[j][i] * a[i-j-1];
			}
		}
		dummy(a, b, c, d, e, aa, bb, cc, 0.);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S118\t %.2f \t\t", clock_dif_sec);;
	check(1);
	return 0;
}

void reference_s118(int *arg_a, const int *arg_bb, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    reference_storage_bb = arg_bb;
    original_s118(arg_ld);
}
