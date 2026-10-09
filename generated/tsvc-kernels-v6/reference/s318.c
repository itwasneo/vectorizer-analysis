/* TEST ONLY: original s318 with its harness disabled, not the extracted kernel.
 * Retains the original global names, declarations, computational statements and
 * epilogue. LEN/LEN2 are bound at runtime; nl executes exactly once.
 * Do not send this file to the LLM or use it for performance measurement.
 */
#include <time.h>
#include <stdlib.h>
#define TYPE int
#define LEN reference_n
#define lll LEN
#define clock() ((clock_t)0)
#define init(...) ((void)0)
#define check(...) ((void)0)
#define printf(...) ((void)0)
#define dummy(_a,_b,_c,_d,_e,_aa,_bb,_cc,_scalar) (reference_last_scalar = (_scalar), reference_output_max = (max), reference_output_index = (index), reference_output_chksum = (chksum))
static int reference_n;
static int reference_last_scalar;
static int temp;
static const int *a;
static int reference_output_max;
static int reference_output_index;
static int reference_output_chksum;

#define FABS(value) abs(value)


int original_s318( int inc)
{

//	reductions
//	isamax, max absolute value, increments not equal to 1


	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s318 ");
	start_t = clock();

	int k, index;
	TYPE max, chksum;
	for (int nl = 0; nl < 1; nl++) {
		k = 0;
		index = 0;
		max = FABS(a[0]);
		k += inc;
		for (int i = 1; i < LEN; i++) {
			if (FABS(a[k]) <= max) {
				goto L5;
			}
			index = i;
			max = FABS(a[k]);
L5:
			k += inc;
		}
		chksum = max + (TYPE) index;
		dummy(a, b, c, d, e, aa, bb, cc, chksum);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S318\t %.2f \t\t", clock_dif_sec);;
	temp = max + index+1;
	check(-1);
	return 0;
}

int reference_s318(const int *arg_a, int *arg_out_max, int *arg_out_index, int *arg_out_chksum, int arg_inc, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    original_s318(arg_inc);
    *arg_out_max = reference_output_max;
    *arg_out_index = reference_output_index;
    *arg_out_chksum = reference_output_chksum;
    return temp;
}
