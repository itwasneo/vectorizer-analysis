/* TEST ONLY: original s331 with its harness disabled, not the extracted kernel.
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
#define dummy(_a,_b,_c,_d,_e,_aa,_bb,_cc,_scalar) (reference_last_scalar = (_scalar), reference_output_j = (j), reference_output_chksum = (chksum))
static int reference_n;
static int reference_last_scalar;
static int temp;
static const int *a;
static int reference_output_j;
static int reference_output_chksum;

int original_s331()
{

//	search loops
//	if to last-1

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s331 ");
	start_t = clock();

	int j;
	TYPE chksum;
	for (int nl = 0; nl < 1; nl++) {
		j = -1;
		for (int i = 0; i < LEN; i++) {
			if (a[i] < (TYPE)0.) {
				j = i;
			}
		}
		chksum = (TYPE) j;
		dummy(a, b, c, d, e, aa, bb, cc, chksum);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S331\t %.2f \t\t", clock_dif_sec);;
	temp = j+1;
	check(-1);
	return 0;
}

int reference_s331(const int *arg_a, int *arg_out_j, int *arg_out_chksum, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    original_s331();
    *arg_out_j = reference_output_j;
    *arg_out_chksum = reference_output_chksum;
    return temp;
}
