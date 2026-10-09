/* TEST ONLY: original s13110 with its harness disabled, not the extracted kernel.
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
#define dummy(_a,_b,_c,_d,_e,_aa,_bb,_cc,_scalar) (reference_last_scalar = (_scalar), reference_output_max = (max), reference_output_xindex = (xindex), reference_output_yindex = (yindex), reference_output_chksum = (chksum))
static int reference_n;
static int reference_last_scalar;
static int temp;
static const int *reference_storage_aa;
static int reference_output_max;
static int reference_output_xindex;
static int reference_output_yindex;
static int reference_output_chksum;

int original_s13110(int reference_ld) {
    const int (*aa)[reference_ld] = (const int (*)[reference_ld])reference_storage_aa;

//	reductions
//	if to max with index reductio 2 dimensions

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s3110");
	start_t = clock();

	int xindex, yindex;
	TYPE max, chksum;
	for (int nl = 0; nl < 1; nl++) {
		max = aa[(0)][0];
		xindex = 0;
		yindex = 0;
		for (int i = 0; i < LEN2; i++) {
			for (int j = 0; j < LEN2; j++) {
				if (aa[i][j] > max) {
					max = aa[i][j];
				}
			}
		}
		chksum = max + (TYPE) xindex + (TYPE) yindex;
		dummy(a, b, c, d, e, aa, bb, cc, chksum);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S13110\t %.2f \t\t", clock_dif_sec);;
	temp = max + xindex+1 + yindex+1;
	check(-1);
	return 0;
}

int reference_s13110(const int *arg_aa, int *arg_out_max, int *arg_out_xindex, int *arg_out_yindex, int *arg_out_chksum, int arg_n, int arg_ld) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    reference_storage_aa = arg_aa;
    original_s13110(arg_ld);
    *arg_out_max = reference_output_max;
    *arg_out_xindex = reference_output_xindex;
    *arg_out_yindex = reference_output_yindex;
    *arg_out_chksum = reference_output_chksum;
    return temp;
}
