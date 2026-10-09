/* TEST ONLY: original s314 with its harness disabled, not the extracted kernel.
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

int original_s314()
{

//	reductions
//	if to max reduction

	clock_t start_t, end_t, clock_dif; double clock_dif_sec;


	init( "s314 ");
	start_t = clock();

	TYPE x;
	for (int nl = 0; nl < 1; nl++) {
		x = a[0];
		for (int i = 0; i < LEN; i++) {
			if (a[i] > x) {
				x = a[i];
			}
		}
		dummy(a, b, c, d, e, aa, bb, cc, x);
	}
	end_t = clock(); clock_dif = end_t - start_t;
	clock_dif_sec = (double) (clock_dif/1000000.0);
	printf("S314\t %.2f \t\t", clock_dif_sec);;
	temp = x;
	check(-1);
	return 0;
}

int reference_s314(const int *arg_a, int arg_n) {
    reference_n = arg_n;
    reference_last_scalar = 0;
    a = arg_a;
    original_s314();
    return temp;
}
