# Final 15 TSVC cases: adaptation review

The v6 dataset completes all **151 local benchmarks**, but completeness does not
mean equivalence to the original floating-point programs or 151 equally useful
integer-vectorization tasks. This document records the decisions for the final
15, in addition to the [common contracts](tsvc-kernels.md).

## Kernelization versus semantic adaptation

Common kernelization removes benchmark initialization/timing/repetition, exposes
storage and outputs, and parameterizes bounds. We retain the computational
statements and dependencies, subject to the documented integer interpretation.
Changing `TYPE` to `int`, changing an exit into an API outcome, or choosing a
valid storage domain are **semantic adaptations**, not merely wrapper changes.

Every evaluated signed intermediate **in the reference computation on the
executed path** must fit `int`. This is not permission for a candidate to introduce
new overflowing intermediates or evaluate invalid operations past an early stop.
Overflow-safe tester recipes do not narrow the caller's permitted input values.

The earlier 136 kernel files, reference files, and signatures are unchanged in
v6. The source snapshot/hash gate is unchanged. New rewrite sites have exact
recipe checks; accepting these cases does not enable arbitrary fractional
literals, library calls, preprocessor branches, or post-loop computations.

## Decisions by case

| Cases | Decision and observable behavior |
| --- | --- |
| `s115` | Preserve the triangular SAXPY recurrence and `aa[j][i]`, including reads of previously updated `a[j]`. Square `n, ld` interface. |
| `s118` | Preserve `bb[j][i] * a[i-j-1]` and sequential dot-product recurrence. Do not replace the predecessor by `a[j]`. |
| `s232` | Preserve triangular row-wise repeated squaring plus `bb[j][i]`. Do not update the upper triangle or padding. |
| `s2111` | Preserve left/up wavefront dependencies, the subsequent full logical-matrix sum, and the original **zero-checksum-to-3 fallback**. Return 3 even for `n=0`; arrays remain unchanged for that empty call. |
| `s254`, `s255` | The explicit `(TYPE).5` / `(TYPE).333` casts become integer zero. The resulting stores are zero, not integer averages. Preserve carry setup and evaluated additions; require `n>=1` / `n>=2` respectively. |
| `s291`, `s292` | Same zero-valued cast policy, preserving wraparound indices. Both admit `n=0`; `s292` **excludes only `n=1`**, because `b[LEN-2]` would be out of bounds in the first iteration. |
| `s317` | `(TYPE).99` becomes zero. Preserve the `n/2`-trip product structure. Return **1 for `n=0` or `n=1`**, otherwise 0. There are no array arguments. |
| `s315` | Remove the exact pre-timer `a[i]=(i*7)%LEN` initializer; the caller supplies `a`. Require `n>=1`. Preserve the first maximum on ties. Expose `x`, zero-based `index`, and `chksum=x+index`; separately return the original **`index+x+1`**, with its original evaluation order. |
| `s318` | Require `n>=1` and `0<=inc<=INT_MAX/n`. Supply `max(1,n*inc)` initialized elements, including gaps; exclude `INT_MIN`. Preserve the first absolute maximum, logical iteration index (not physical offset), dummy checksum, and **`max+index+1`** return. `inc=0` repeatedly reads `a[0]`; the final `k+=inc` must also fit. |
| `s258`, `vbor` | Treat `aa[0][i]` as one **valid row of `n` columns**, with `ld>=max(1,n)` and `ld` initialized elements. Preserve `s258`'s carried scalar and all staged `vbor` products. `vbor` also returns its original post-loop sum. |
| `s451` | Integer storage, but **double-precision `sin`/`cos` and addition** followed by a single truncation toward zero to `int`. Select the original `#else` branch, not `sinf`/`cosf`. This is deliberately not a pure-integer kernel. |
| `s481` | Replace `exit(0)` with a returned outcome: **first negative `d` index**, or **-1 on completion**. Stop before updating `a[i]`; preserve that element and the suffix. `n=0` returns -1. This does not terminate the caller's process. |

### Why not change the fractional factors to division?

`(int).5` is zero in C. Replacing `sum * (int).5` with `sum/2` would invent a
different integer algorithm. We chose literal cast semantics and explicitly
classified these five cases as **degenerate integer adaptations**. The generator
retains the loop/carry structure and replaces only the reviewed cast by zero;
the reference leaves the fractional cast for the C compiler to evaluate.
The evaluated sums still have signed-representability preconditions even though
the final product is zero. Compiler elimination of these computations is legal
for valid inputs and should not be mistaken for a meaningful SIMD improvement.

A future fixed-point or rational-scaling dataset would be a separate numerical
policy and a separate dataset, not an unannounced correction to these files.

### First-row extents are not a cross-row memory walk

The original `aa[0][i]` expressions range over `LEN`, although the declared row
width is `LEN2`. When `LEN>LEN2`, indexing beyond that row is not a defined C row
access merely because the larger enclosing matrix has enough bytes.

The adaptation supplies a valid row rather than reproducing that behavior or
assuming `LEN==LEN2`. Kernels use flat indexing; references retain `aa[0][i]`
with a pointer-to-VLA row width of `ld`. The contract's `logical_rows=1` controls
allocation and padding checks. At `n=0`, the whole physical row is unused padding.
These two cases use `--matrix-sizes`, but the size is a **column count**, not a
square dimension. Their kernel bound is `INT_MAX/2`; the tester caps it at 128.

### Libm and termination are explicit interface choices

`s451` requires binary64 evaluation, the default floating-point environment,
strict math, and the same conforming libm on both sides. The checker links `-lm`
when this case is selected. Integer arguments convert exactly to double; the
finite sum lies in `[-2,2]`, making its final integer conversion representable.
Truncating each term separately is **not** equivalent to truncating their sum.
`errno` and floating-point exception flags are outside the observable interface.
No cross-libm bitwise guarantee or vector-math approximation tolerance is implied.
The reference retains the original conditional and explicitly selects its double
branch. Alive2 integration will need an appropriate library model or an explicit
unsupported/inconclusive classification.

`s481`'s returned index preserves the stop location and array state, **not process
semantics** such as `atexit` handlers and stream flushing. A caller can choose to
exit on this signal. The reference keeps the original `exit(0)` call site, using
a test-only macro to record the index and return from the original function.
The kernel instead returns directly at that site. Inputs at and after the stop
need not make a hypothetical skipped update overflow-safe.

## Nontrivial, overflow-safe test profiles

These recipes are recorded under `testing`, with `contract_restriction: false`:

- **`s115` / `s118`:** full `[-3,3]` coefficients through `n=8`. At larger sizes,
  each active matrix column has at most one unit-magnitude coefficient. Starting
  vectors remain in `[-3,3]`, giving `|a[i]|<=3*(i+1)`. Coefficient position and
  sign vary; unused matrix elements and padding remain intact.
- **`s232`:** full `[-3,3]` inputs through `n=5`. Beyond that, choose bounded
  desired row outputs and construct each `bb` as `target-previous*previous`.
  The initial `aa` is not overwritten by the preparer; nontrivial changes and
  the untouched triangle/padding are tested. Result magnitudes stay at most 3.
- **`s2111`:** full `[-3,3]` inputs through `n=8`. For larger matrices, initialize
  only the top/left boundaries from the six-period sequence
  `[u,v,v-u,-u,-v,u-v]`, with `u,v` in `[-3,3]`. It obeys
  `f(k-1)+f(k+1)=f(k)`, so the wavefront `f(column-row)` remains bounded by 6.
  Interior inputs remain independent and are overwritten by the real recurrence.
  Both ordinary sums and the zero-to-three fallback are exercised.
- **`vbor`:** logical inputs in `[-2,2]`, including uniform +2/-2 trials. A single
  output has magnitude at most `10*6*3*1*2^12 = 737280`; with test `n<=128`, any
  checksum prefix is bounded by 94371840. Padding canaries are not clamped.
- **`s451`:** small mixed-sign values plus +/-1000, `INT_MIN`, and `INT_MAX`.
- **`s481`:** all four stop patterns (none, first, middle, last) for every data
  trial, independent of the data values. Later data remain initialized;
  hand-computed tests put overflowing hypothetical updates past the stop.

Regression tests also evaluate profile bounds using checked 64-bit intermediates,
then confirm representability before narrowing. These are tests of the recipes,
not a general proof of all caller inputs.

## Reporting policy and evidence

Manifest schema **6** adds size exclusions, single-row extents, numeric and
termination contracts, and case-level `experiment_caveats`. The checker accepts
schemas 1–6. The five degenerate cases, the libm case, the termination case, and
the two single-row generalizations have explicit caveat flags: **report them
separately rather than silently pooling them into an ordinary integer speedup
aggregate**. The other cases remain integer adaptations too; absence of this
additional flag is not a claim of floating-point equivalence.

Validation recorded on the development machine:

- **90 regression tests** passed, including deliberately incorrect candidates.
- **144,072** default ASan/UBSan differential executions across all 151 cases.
- **14,544** additional executions for the final 15, seed 42, vector sizes through
  4096, matrix sizes through 128, and stride paddings 0/1/5/64.
- The saved 136-case v5 dataset passed its **129,960** executions again.
- All 151 kernels passed strict C11 syntax checking; fresh generation matched v6.

Reports: `generated/tsvc-kernels-v6/validation-report.json`,
`generated/tsvc-kernels-v6/validation-final-large.json`, and
`generated/tsvc-kernels-v5/validation-schema6-regression.json`.
These machine-specific reports are local artifacts, not committed files. The
frozen v6 kernels/references/contracts are committed; rerun the checker on the
execution host to produce that machine's report.

These are finite differential-test results against the documented adapted
references, **not formal verification or equivalence to unmodified floating-point
TSVC**. Candidate generation/repair, explicit Alive2 assumptions, and AVX2 host
benchmarking remain subsequent workflow stages.
