# Parameterized TSVC integer kernels

## Current status

The generator inventories and emits **all 151 distinct TSVC benchmarks** across
18 categories: **122 one-dimensional, 27 square-matrix, and 2 single-row cases**.
There are no remaining `needs_review` cases in this snapshot. Nine use explicit
index buffers, six have derived pointer views, and one uses arbitrary-integer
switch selectors.

**These are adaptations, not unchanged floating-point algorithms in wrappers.**
Five fractional-cast cases become degenerate; `s451` retains double libm arithmetic
with integer storage; `s481` returns a stop outcome instead of exiting; two cases
have explicit valid-row extent adaptations. See the
[final-case semantic review and reporting policy](tsvc-final-adaptations.md), and
the [implementation plan](tsvc-parameterization-plan.md) for subsequent workflow stages.

The earlier `scripts/extract_tsvc_int.py` and `generated/tsvc-int/` whole-program
adaptations are unchanged. The new generator reads the original `tsc.inc`
directly, avoiding those adaptations' fractional initializers and generic harness
checksums. Explicitly reviewed post-loop observations are retained as described below.

## Use the committed dataset

`generated/tsvc-kernels-v6/` is a frozen snapshot included in Git: 151 kernel files,
151 reference files, 151 contracts, plus `kernels.h`, `manifest.json`, `LICENSE.TXT`,
and its README. Pulling this repository supplies everything the differential
checker needs, apart from Python 3.10+, Clang with ASan/UBSan, and libm. The upstream
TSVC checkout and an LLM are **not required** to test the bundled kernels or
candidates against the bundled references. See [test extraction](#test-extraction).

Only v6 is versioned. The earlier 35-case `generated/tsvc-kernels/`, 54-case
`generated/tsvc-kernels-v2/`, 71-case `generated/tsvc-kernels-v3/`, 92-case
`generated/tsvc-kernels-v4/`, and 136-case `generated/tsvc-kernels-v5/` outputs are
preserved locally and ignored by Git, as are all machine-specific validation
reports. The generator/checker defaults still point to `generated/tsvc-kernels/`;
select the desired directory explicitly.

## Regenerate or run generator regression tests

These operations require the pinned source checkout. No Python packages, LLVM
Python bindings, Alive2, or x86 host are required for generation. From the project
root, if `llvm-test-suite/` does not already exist:

```sh
git clone --filter=blob:none --no-checkout \
  https://github.com/llvm/llvm-test-suite.git llvm-test-suite
git -C llvm-test-suite sparse-checkout set MultiSource/Benchmarks/TSVC
git -C llvm-test-suite checkout --detach 7e8512d48c9735d514124a62ed3863a800337aad

# Output must be new/empty; never overwrite the committed v6 snapshot.
python3 scripts/generate_tsvc_kernels.py --output generated/tsvc-kernels-regenerated
python3 -m unittest discover -s tests -v
```

The sparse checkout avoids downloading unrelated test-suite file contents.
Without this source, source-dependent Python tests are skipped; such a run is
**not** the complete 90-test regression result. Ordinary differential checking
of the committed dataset does not have this dependency.

Each output directory contains:

```text
manifest.json          All 151 cases, source hashes/locations, status and contracts
kernels.h              Prototypes for the supported interfaces
kernels/s124.c         Computational function, not an executable/main()
contracts/s124.json    Interface, bounds, access modes and explicit assumptions
reference/s124.c       Test-only adapter around the original TSVC function
LICENSE.TXT           Copied upstream license for adapted/copied TSVC source
```

**The destination must be absent or empty.** Generation refuses to overwrite an
existing dataset/candidates or mix stale files into a newer inventory. Use a new
`--output` directory when regenerating. Nothing in `llvm-test-suite` is modified.

The reviewed snapshot's `tsc.inc` SHA256 is:

```text
4a90a9a5470e635d5a3bcffe53816ce1b1ef2cefe15782567debe8f727908ecb
```

It was inspected at llvm-test-suite commit
`7e8512d48c9735d514124a62ed3863a800337aad`. Source changes cause generation to fail
before writing any files. The extractor handles this known source layout; it is
not a general C parser. Don't just update the hash to bypass an error: review
changes and update recipes/tests first.

## Meaning of a kernel

For example, the generated interface is:

```c
void s124(int *a, const int *b, const int *c,
          const int *d, const int *e, int n);
```

The function retains the original `j = -1` and conditional loop, with `LEN`
replaced by `n`. It does **one computational repetition**. The caller owns
allocation, initialization, repetitions, output comparison, and timing.

Scalar inputs remain parameters, e.g. `s272(..., int t, int n)` and
`vpvts(..., int s, int n)`. Scalar reductions become explicit return values:

```c
int vsumr(const int *a, int n);
int vdotr(const int *a, const int *b, int n);
```

This is an integer adaptation, not a claim of equivalence to floating-point TSVC
or of identity with the paper's 149 functions. We retain traversal, statement,
branch, partial-write, and tail structure except for the explicit adaptations
listed in each contract. Retaining structure does not guarantee preservation of
the original numeric problem: notably the five zero-valued fractional casts lose
their floating-point purpose. The extractor does not vectorize loops. A block
formerly inside the repetition loop remains a scope; the repetition is removed.

### Square matrix interfaces

For example:

```c
void s114(int *aa, const int *bb, int n, int ld);
void s125(const int *aa, int *array, const int *bb, const int *cc, int n, int ld);
```

- `n` is the **logical square side length**, replacing `LEN2`; it is not an
  independent row/column pair. Transposes and triangular domains remain square.
- `ld` is the shared **physical row stride in integers**, not bytes, and must be
  at least `max(1, n)`. `ld == n` is compact storage for nonempty matrices;
  larger strides introduce padding that must remain unchanged.
- Kernels use flat buffers and accesses such as
  `aa[(size_t)i * ld + j]`. The cast prevents intermediate signed multiplication
  overflow in address calculations; callers must supply the contracted extent.
- A matrix needs at least `max(1, n*ld)` initialized integers. Contiguous packed
  buffers (e.g. `array` in `s125`, `s126`, `s141`) instead need `max(1, n*n)`.
  Associated 1D vectors need `max(1, n)`. **Packed storage does not use `ld`.**
- `s141` uses triangular packed indices in that contiguous allocation; its unused
  suffix is preserved. `s132` accesses its fixed row/column 1 only when `n>=2`.
- Square-matrix `n` is bounded by 46340, keeping `n*n`, original integer index
  expressions, and final induction-variable increments in range. `ld` is bounded
  by `INT_MAX`; the mathematical `n*ld*sizeof(int)` must also fit in `SIZE_MAX`
  and the supplied allocation.

**Single-row exception:** `s258` and `vbor` expose `aa` as one row of `n` columns,
not an `n*n` matrix. Provide `ld>=max(1,n)` and `ld` initialized integers; columns
`[n,ld)` are untouched padding, including the whole row at `n=0`. Their `n` bound
is `INT_MAX/2`, and `ld*sizeof(int)` must fit the allocation and `SIZE_MAX`.
References retain `aa[0][i]` with physical row width `ld`. This deliberately avoids
out-of-row accesses when the original `LEN` exceeds `LEN2`; it does not simulate
a flattened cross-row memory walk. The checker uses `--matrix-sizes` for these
column counts as well as square side lengths.

Contracts record each buffer's layout and the row-stride relationship. Schema 2
introduced these fields; schema 3 added index/scalar domains and offset-vector
extents. Schema 4 added scalar output slots, result expressions, helper provenance,
integer value domains, and separate test-input profiles. Schema 5 added pointer
views, extended/strided buffers, selectors, and reviewed post-loop work. Current
schema **6** adds excluded sizes, single-row extents, numeric/termination contracts,
and experiment caveats. The checker still accepts schemas 1 through 5.

### Indirect addressing and scalar outputs

Index buffers are explicit `const int *ip` parameters. For every `0 <= i < n`,
require `0 <= ip[i] < n`. This does **not** require a permutation: duplicates and
arbitrary order are allowed. Repeated scatter destinations preserve sequential
**last-store-wins** semantics. Index buffers are disjoint from all data buffers
and are compared after every run to detect unintended modification.

There are a few case-specific contracts:

| Case | Contract / observable outputs |
| --- | --- |
| `s4114` | `1 <= n1 <= n+1`; the 1-based start `n1=n+1` selects an empty loop. Preserve the reversed `c[n-ip[i]-1]` access. |
| `s4116` | Square matrix with `n, ld`; `1 <= j <= max(1,n)` and `0 <= inc <= INT_MAX-n`. `inc` is an offset, **not** a stride. Buffer `a` needs `max(1,n+inc)` integers. Only `n-1` terms are summed. |
| `s353` | `n % 5 == 0`, because the original loop is unrolled by five and has no tail. No rounding or tail invention. `c[0]` must be initialized even at `n=0`. |
| `s314`, `s316` | `n >= 1`; return max/min initialized from `a[0]`, with no invented empty identity. |
| `s3112` | Return the final sum **and** write the complete prefix-sum array `b`; both are checked. |

For example:

```c
void vas(int *a, const int *b, const int *ip, int n);
int s4116(const int *a, const int *aa, const int *ip,
          int j, int inc, int n, int ld);
```

The extraction recipe records where a scalar result is observed. `s4115` and
`s4116` pass a constant zero to `dummy()` but save their real sum in global
`temp`. The kernel returns `sum`, while the reference returns the original
`temp`; returning the dummy argument would incorrectly erase the computation.
Reviewed reductions exposed only through `dummy`, such as `s311`, also return
explicit scalar results.

### Helpers and multiple scalar observations

The generated files include private, parameterized copies of the reviewed leaf
helpers for `s151`, `s152`, `s31111`, `s4121`, and `s471` (including its original
no-argument, no-op helper). Helper bodies come from the pinned
source and have recorded hashes. No unresolved external helper is left for the
caller. Calls and loop structure are retained rather than manually inlined.
The references keep original helper bodies and `LEN` indexing; array parameters
are pointers so an empty call does not evaluate a zero-length VLA bound.
Unreviewed helper interfaces and transitive calls are rejected.

**`s31111` is a fixed 32-element reduction**, not a general sum over `n`: it calls
its four-element helper eight times. Its contract requires `n>=32`; larger
buffers have an unused suffix. Do not replace its fixed bounds with `n`.

Some cases now expose local scalar state through output pointers, in addition to
returning the original `temp` observation. Each output slot holds one initialized
`int`, must be valid, and must be disjoint from every other buffer/slot:

```c
int s3110(const int *aa, int *out_max, int *out_xindex,
          int *out_yindex, int *out_chksum, int n, int ld);
int s332(const int *a, int *out_index, int *out_chksum, int t, int n);
```

- `s3110`: first row-major maximum on ties, with zero-based coordinates. The
  dummy checksum is `max+xindex+yindex`; the return preserves the original
  **`max + xindex+1 + yindex+1`** expression and evaluation order.
- `s13110`: the original coordinates remain zero, even when a later maximum is
  found. This is deliberately **not changed into an argmax**. Both matrix
  extrema require `n>=1`; all checksum intermediates must also fit in `int`.
- `s331`: last negative element, not first. Return its 1-based position, or zero
  if absent. `out_j` and `out_chksum` hold the zero-based index, or `-1`.
- `s332`: first value strictly greater than `t`. No match (including empty input)
  returns `-1`, with index `-2` and checksum `-3`; preserve these original sentinels.
- `s312`: the empty product returns **1**, not zero.
- `s3113`: integer absolute-value maximum; require `n>=1` and exclude `INT_MIN`.
  The kernel uses an integer conditional helper; the reference uses standard
  integer `abs`, not floating-point `fabs`/`fabsf`.
- `s351` and `s352`: like `s353`, retain five-way unrolling and require `n%5==0`.
  `s351` still reads its initialized `c[0]` at `n=0`.
- `s343`: conditional **column-major** packing from `aa[j][i]`, not row-major
  packing. The contiguous output suffix remains unchanged.

The output-pointer adaptation makes the reviewed scalar state observable, not
just a combined checksum. References capture these locals at the original dummy
call and retain the original post-loop `temp` computation. Every slot is checked
with exact and guarded allocations, even if the return value is correct.

### Shared storage, symbolic strides, and selectors

**Derived pointers are not additional independent inputs.** Equivalencing cases
receive one backing buffer per storage object. They retain pointer assignments
and overlapping accesses inside the function; the tester likewise allocates and
compares each backing buffer once. The original pointer `restrict` annotations
are not carried into these views. Distinct backing arguments remain disjoint,
while views of one backing buffer may alias it and each other.

| Case | Backing storage and initial view | Required initialized backing extent |
| --- | --- | --- |
| `s421` | `yy = xx` | `xx`: `max(1,n)` |
| `s1421` | `xx = b + n/2` | `b`: `max(1,n)`; read upper half, write lower half |
| `s422` | `xx = array + 4` | `array`: `max(1,n+8)` |
| `s423` | `xx = array + 64` | `array`: `max(1,n+64)` |
| `s424` | `xx = array + 63` | `array`: `max(1,n+63)` |

For example:

```c
int s424(const int *a, int *array, int n);
```

`s424` writes `array[i+64]` from `array[i]`, so later reads must observe earlier
writes. **Snapshotting the input is incorrect.** The first feedback iteration
occurs at `n=66`. Its post-loop sum includes `array[63]`, which the main loop
never writes. At `n=0`, the contracted extra storage still permits forming its
one-past view, but there are no dereferences or writes.

`s1351` keeps its advancing local `A`, `B`, and `C` pointers, with read-only
qualifiers where appropriate and without `restrict`. It has no divisibility
requirement and supports empty calls.

Only exact, recipe-listed `set1d(...)` benchmark initializers are removed; the
caller supplies the initial buffer contents. Binding statements and constants
such as `vl=63` remain. Unknown initializers, bindings, or setup constants fail
extraction rather than being silently discarded.

**Observed post-loop sums are deliberately retained.** The five equivalencing
cases and `s471` return their original `temp` sums as local integer checksums.
These sums originally ran after the timer: these particular interfaces therefore
mean one computational repetition **plus the listed post-loop observation**, not
just the historical timed region. The harness `check()`/printing is still absent.
This choice is explicit in each contract; all sum intermediates must fit `int`.
References retain the original post-loop statements and global `temp`, rather
than sharing the kernel's local-checksum rewrite.

Symbolic access contracts distinguish loop steps from memory strides/offsets:

| Case | Scalar domain and storage |
| --- | --- |
| `s122`, `s172` | `1 <= n1 <= n+1`, `1 <= n3 <= INT_MAX-n`. The latter bound also protects the final induction increment. `n1=n+1` is empty. |
| `s174` | `0 <= M <= n/2`; preserve elements beyond the two `M`-element halves. |
| `s162` | `INT_MIN <= k <= INT_MAX-n`; `k<=0` does no work. Buffer `a` needs `max(1,n+max(0,k))` elements. |
| `s171` | `0 <= inc <= INT_MAX/max(1,n)`; `a` needs `max(1,n*inc)` elements. `inc=0` repeatedly updates **the same `a[0]`**, not an empty loop. |
| `s175` | `1 <= inc <= INT_MAX-n`; `a` needs `max(1,n+inc)` elements because the final look-ahead read may be beyond logical `n`. |

Extended elements and stride gaps must remain unchanged unless the original
computation writes them. Required allocation bytes must fit `SIZE_MAX`; sizes
are mathematical extents, not permission to wrap allocation arithmetic.

`s442`'s read-only `indx` buffer contains **switch selectors, not array addresses**.
Any signed integer is valid. Values `1..4` choose their named labels; every other
value falls through to the case-1 computation. The tester runs nine selector
patterns independently of data trials, including case 4, out-of-range values,
`INT_MIN`, and `INT_MAX`.

### Final reductions and numeric/control outcomes

- `s315`: the caller supplies `a`; the exact pre-timer `(i*7)%LEN` initializer is
  removed. Require `n>=1`. Expose maximum `x`, first zero-based `index`, and dummy
  `chksum`; separately return the original `index+x+1` expression.
- `s318`: first absolute maximum among `a[i*inc]`, with a **logical** index rather
  than physical offset. Require `n>=1`, `0<=inc<=INT_MAX/n`, and `max(1,n*inc)`
  initialized elements, all excluding `INT_MIN`. Zero stride is valid. Expose
  max/index/checksum and return `max+index+1`. Protect the final `k+=inc` too.
- `s254`, `s255`, `s291`, `s292`, `s317`: reviewed fractional casts truncate to
  zero, **not division or fixed-point scaling**. These cases are marked degenerate.
  `s254` requires `n>=1`, `s255` requires `n>=2`; `s292` admits zero but excludes
  one. `s317` returns one for `n=0/1`, zero otherwise, and takes no arrays.
- `s2111`: return the post-loop matrix sum, substituting **3 when the sum is 0**,
  including an empty call. Preserve the original fallback.
- `s451`: exact integer-to-binary64 arguments, double `sin`/`cos` and addition,
  then a single truncation to `int`. Requires strict math and libm (`-lm`), not
  `sinf`/`cosf` or separate term truncations. This is an integer-storage, mixed
  arithmetic case. `errno`/FP exception flags are outside its observable interface.
- `s481`: return the first negative `d` index **before** its update, or -1 if
  completed. Keep prefix writes and the untouched stop element/suffix. This is a
  returned outcome, not process termination; skipped updates need not be safe
  if hypothetically evaluated.

The manifest marks five degenerate casts, one mixed-libm case, one termination
adaptation, and two row-extent generalizations under `experiment_caveats`. Report
these nine cases separately rather than silently pooling them into an ordinary
integer speedup aggregate. [Full rationale and profiles](tsvc-final-adaptations.md).

### Common contract

- `int` must be signed 32-bit (checked at compile time).
- Most 1D cases admit `0 <= n <= INT_MAX/2`. Square matrices use the tighter bound
  above; single-row cases use the 1D bound. Min/max and absolute-max cases require `n>=1`, `s31111` requires
  `n>=32`, and `s351`/`s352`/`s353` require multiples of five. There is **no
  divisibility-by-eight requirement**.
- Each array is a valid initialized buffer of its contracted extent, including
  when `n == 0`. Ordinary vectors need at least one element at zero; extended
  backing buffers still require their listed extra storage. No alignment beyond
  normal `int` alignment is required.
- Distinct exposed backing-buffer arguments use **non-overlapping storage**.
  Derived views share their backing object as listed above; they are not separate
  arguments. We don't introduce `restrict`. `const` describes access through a
  pointer, not disjointness.
- Every evaluated signed arithmetic intermediate in the reference computation's
  executed path must fit in `int`. A candidate may not introduce new overflow or
  invalid operations on a skipped path. There is no `-fwrapv`, saturation, or
  implicit conversion to unsigned arithmetic.
- Untouched array elements remain observable. Compare complete arrays, not just
  the indices that the loop is expected to update.
- Where empty inputs are admitted, data arrays are unchanged. Sum/dot-product
  reductions ordinarily return zero; products return one; searches have the
  case-specific sentinels above. Exceptions include `s2111`'s return of 3 and
  `s481`'s return of -1. Scalar output slots are still written. Min/max exclude
  empty input. Some other cases have explicit minimum or excluded sizes.

Contracts are requirements on the caller; the functions do not check them at
runtime. They also are **not yet encoded as Alive2 assumptions**. Memory/aliasing
contracts must be modeled explicitly when formal validation is added.

## Test extraction

The test runner requires Clang or a compatible C11 compiler, plus libm for `s451`.
It adds `-lm` when a selected contract requires it. This scalar testing
can run on ARM or x86; it is not AVX2 performance reproduction.

```sh
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 \
  --sanitize \
  --report generated/tsvc-kernels-v6/validation-report.json

# Select a 1D subset or use another compiler/seed:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 \
  --case s124 --case vsumr --cc clang --seed 42 \
  --sizes 0 1 7 8 9 15 16 17 --sanitize

# Matrix dimensions and padding are selected independently:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 --case s114 --case s125 \
  --matrix-sizes 0 1 2 7 8 9 17 --stride-paddings 0 1 5 --sanitize

# Repeated scatter destinations and the explicitly five-way-unrolled loop:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 --case vas --case s353 \
  --sizes 0 1 5 10 15 40 --sanitize

# Fixed helper bounds and safe product/recurrence profiles:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 --case s31111 --case s312 --case s322 \
  --sizes 0 1 8 9 18 19 32 33 4096 --seed 42 --sanitize

# Shared-storage dependencies, offsets/strides, and arbitrary switch selectors:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 --case s424 --case s171 --case s442 \
  --sizes 0 1 63 64 65 66 67 129 --sanitize

# Safe nonlinear profiles and independently sized single-row storage:
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 --case s232 --case s2111 --case vbor \
  --matrix-sizes 0 1 5 6 8 9 128 --stride-paddings 0 1 5 64 --sanitize

python3 -m unittest discover -s tests -v
```

Default coverage is **144,072 differential executions across 151 kernels**:

- 122 1D kernels use a requested grid of 27 sizes from 0 through 257, including
  10/11 and 66/67 to exercise branch/dependence boundaries.
- 29 matrix cases (27 square and two single-row) use 15 logical sizes from 0
  through 33, each with `ld = max(1,n) + padding` for padding 0, 1 and 5.
- Both groups use 12 deterministic trials and exact as well as guarded allocations.
- Each indexed case runs **six index patterns for every trial**: identity,
  reverse, all-zero, all-last, seeded permutation, and random with replacement.
- `s442` runs nine independent selector patterns per trial. Selector patterns
  do not impose the `[0,n)` restriction used by gather/scatter indices.
- `s481` runs all four stop patterns (none, first, middle, last) for every data
  trial. The returned outcome and complete array state are both compared.

Requested sizes are intersected with **each case's contract**, never rounded.
For example, default `s353` sizes are `[0,5,10,15,40,65]`, min/max cases omit zero,
and `s31111` uses only requested sizes at least 32. `s292` excludes one but not zero.
The CLI prints exclusions, and the report records `tested_sizes` and
`excluded_sizes` per case. A selected case with no eligible requested sizes is
an error, not a vacuous pass.

Logical data include zero, positive, negative, alternating-sign, and seeded
random integers in `[-3,3]`; index values instead satisfy their index domain.
Domain-specific scalar samples exercise first/middle/last rows, empty/nonempty
start ranges, and offsets both below and above `n`. Matrix padding contains
distinct canaries, not zeros.
`--sizes` controls only 1D cases; `--matrix-sizes` controls only matrix cases.
The runner caps these at 4096 and 128 respectively, and stride padding at 64, for
its reviewed test-input/resource domain. These are testing limits, not the
kernel contract bounds.

**Products and recurrences need different input recipes.** Unrestricted random
`[-3,3]` data would overflow at larger sizes. The manifest's `testing` section and
report's `test_profiles` describe these recipes separately from caller contracts:

- `s312`: at most 18 factors have magnitude 2 or 3; others are `-1`, `0`, or `1`.
  Every prefix product has magnitude at most `3^18 = 387,420,489`. Trials include
  large nonzero products, both signs, and a zero partway through the reduction.
- `s321`: for `n>8`, coefficients are in `[-1,1]`, bounding `|a[i]|` by `3*(i+1)`.
- `s322`: for `n>8`, at most one of each pair of coefficients is nonzero, with
  magnitude one. This gives the same linear bound. Small sizes still exercise
  both coefficients simultaneously with full `[-3,3]` inputs.
- `s222`: repeated squares use full `[-3,3]` inputs for `n<=5` (up to `3^16`),
  then constrain only initial `e[0]` to `{-1,0,1}` at larger sizes.
- `s115`/`s118`: full coefficients at small sizes, then sparse unit-magnitude
  coefficients bounding the triangular recurrences.
- `s232`: full small-size inputs, then independently chosen bounded target values
  used to construct the additive terms without overwriting initial `aa`.
- `s2111`: full small-size inputs, then bounded six-period boundary waves with
  independent interior data. Keep the actual wavefront and checksum computation.
- `vbor`: `[-2,2]` logical values, including uniform +/-2, bound both staged
  products and checksum prefixes. Row padding is not clamped.

The [final-case review](tsvc-final-adaptations.md) gives the bounds and construction
rules. Trig trials also include full integer limits, and early-stop patterns are
independent of data trials.

The symbolic start and step samples have periods four and three, exercising all
12 start/step combinations rather than pairing every step of two with an empty
loop. Multiple unrestricted scalar inputs receive distinct value sequences, so
substituting `s1` for `s2` cannot be hidden by identical samples. Zero memory stride
and negative/zero guarded offsets are also exercised.

These are **test-domain restrictions only**, not assumptions that candidates may
make. The kernels still admit any input whose evaluated signed intermediates fit
their contracts. Hand-computed tests also cover larger valid values, absolute
values near integer limits, helper suffix preservation, extrema ties, search
sentinels, and packing order.

The reference adapter retains the original computational statements and control
flow, suppresses initialization/timing/printing, binds `LEN` or `LEN2` to the test
size, and forces `nl` to run once. For matrices, a local pointer-to-VLA alias uses
`ld` as its column extent while preserving **`aa[i][j]`** in the original body.
The oracle therefore does not share the kernel's flattened address expressions.
The two implementations compile in separate translation units, reference at
`-O0` and kernel at `-O2`. Fractional reference casts remain for the compiler to
execute, the trig reference selects the original double branch, and the exit
reference records the stop through a test-only macro at the original call site.

Each implementation receives independent copies of its backing buffers; derived
views within one implementation share those buffers. Tests compare every element of
all buffers, including read-only inputs and scalar output slots, plus scalar
return values. Matrix row
padding is independently checked against its initial canaries, including in the
reference. Guard writes are failures; exact-size allocations allow ASan to detect
out-of-bounds reads as well. The sanitizer option enables both ASan and UBSan
with failure recovery disabled. The JSON report captures hashes,
compiler/version/commands, seed, eligible/excluded sizes, index/selector patterns,
per-case input profiles, scalar-output/pointer-view/single-row/termination cases,
stop patterns, semantic caveats, link libraries, and results. Keep the report with the dataset; generation alone
leaves the manifest's validation status as `not_run`.

Development-machine v6 reports are `validation-report.json` (144,072 executions across all 151
cases) and `validation-final-large.json` (14,544 additional executions across the
final 15, seed 42, vector sizes through 4096 and matrix sizes through 128).
The saved v5 dataset passed 129,960 executions again; its new report is
`generated/tsvc-kernels-v5/validation-schema6-regression.json`. Historical reports
and all earlier datasets remain intact locally. Reports are not committed;
rerun the checker to produce a report for the testing machine and its toolchain.

Passing is **finite differential-test evidence**, not formal verification or an
unbounded guarantee about extraction. The references generalize `LEN`/`LEN2` and
matrix storage too; tests validate our chosen one-repetition integer
interpretation, not original timing
or floating-point results.

### Check a candidate against the reference

Put a candidate with the exact reviewed signature in a separate directory,
named after the case (e.g. `/path/to/candidates/s124.c`):

```sh
python3 scripts/check_tsvc_kernels.py \
  --directory generated/tsvc-kernels-v6 \
  --case s124 --candidate-dir /path/to/candidates --sanitize
```

A conflicting signature is a compile error. Wrong outputs, crashes, sanitizer
findings, timeouts, and compile failures fail the check. The regression suite
includes deliberately incorrect array, reduction, signature, bounds, matrix
stride, transpose, triangular-domain, scatter-order, modified-index, missing
helper-call, wrong scalar-slot, extrema tie-order, snapshotted-alias, modified
extended-tail, wrong-half checksum, switch-default, wrong fractional policy,
trig-conversion, logical-stride-index, and early-stop examples.
It also checks hand-computed packing, identity, gather/scatter, offset dot-product,
min/max, and prefix-sum results without using the reference adapters.
Untrusted generated C must run in an isolated execution environment without
secrets; this script is **not a sandbox**. For AVX2 candidates, use the actual
x86/AVX2 execution environment and add target-specific compilation as part of the
later experiment pipeline; the present runner targets native scalar extraction.

## Current batch and extension policy

Original 1D batch (interfaces and kernel sources unchanged):

```text
s000 s111 s1111 s112 s1112 s113 s1113 s116
s121 s123 s124 s127 s211 s212 s1213 s221 s1221
s271 s272 s273 s274 s276 s277 s278 s279 s453
vif vpv vtv vpvtv vpvts vpvpv vtvtv vsumr vdotr
```

Matrix batch:

```text
s114 s1115 s119 s1119 s125 s126 s132 s141 s231 s1232
s233 s2233 s235 s256 s257 s275 s2275 s2101 s2102
```

Indirect/scalar batch (17 new cases):

```text
s491 s4112 s4113 s4114 s4115 s4116 s4117 va vag vas s353
s311 s313 s3111 s3112 s314 s316
```

Helper/scalar/packing batch (21 new cases):

```text
s151 s152 s31111 s4121 s312 s319 s3113 s3110 s13110 s331 s332
s341 s342 s343 s351 s352 s321 s322 s323 s452 s482
```

1D/symbolics/shared-storage batch (44 new cases):

```text
s128 s131 s161 s1161 s1279 s2710 s2711 s2712 s441 s442 s443
s173 s176 s241 s242 s243 s244 s1244 s2244
s251 s1251 s2251 s3251 s252 s253 s261 s281 s1281 s293 s431
s122 s172 s174 s162 s171 s175 s222 s1351
s421 s1421 s422 s423 s424 s471
```

Final reviewed batch (15 cases):

```text
s115 s118 s232 s254 s255 s258 s291 s292 s2111
s315 s317 s318 s451 s481 vbor
```

All 151 cases now have implementations and contracts. The final-case choices and
experimental limitations are recorded in the linked adaptation review and each
case's contract; none is silently presented as an unchanged floating-point task.

Recipes are in `scripts/tsvc_kernel_specs.py`. Before adding a recipe, review all
accesses, bounds, setup, outputs, helper calls, and the safe test-input domain.
The current transformation intentionally rejects unknown post-loop computation,
unreviewed fractional casts or calls, missing scalar reductions, and mismatched
interfaces. Extend both generator and tests for new patterns. Next are experiment
cohort policy, candidate generation/repair, compatible Clang/Alive2 validation,
and target-host benchmarking, as laid out in the plan.
