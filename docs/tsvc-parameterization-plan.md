# Parameterizing the 151 TSVC benchmarks

**Progress:** 35 initial + 19 matrix + 17 indirect/scalar + 21 helper/scalar/packing
+ 44 1D/symbolics/shared-storage + 15 final cases. **151 generated, 0 `needs_review`.**
All 18 categories are represented by reviewed implementations. See
[usage and contracts](tsvc-kernels.md) and the
[final-case adaptation review](tsvc-final-adaptations.md).
The frozen output `generated/tsvc-kernels-v6/` is included in Git for the testing
host; previous batches and machine-specific reports are preserved locally only.

## Goal and scope

Build our own 151-case, integer-storage TSVC dataset for source-to-source
vectorization. All but `s451` use integer arithmetic; that case deliberately
retains double libm intermediates. Five fractional-cast cases become degenerate
and are marked for separate reporting, not presented as unchanged algorithms. This is **not** a reconstruction of the paper's original
149-case source dataset, which is not present in this repository. The input is the checked-out
`llvm-test-suite/MultiSource/Benchmarks/TSVC/tsc.inc`, not the previously generated
whole-program integer adaptations.

A kernel must have explicit array/scalar inputs and observable outputs, runtime
bounds, and no global state, benchmark data initialization, timing, printing, or
benchmark repetition. Preserve computation order, local setup, branches, and actual nested
computational loops. Removing the outer `nl` timing repetition means a kernel
executes **one repetition's computation**, not the whole benchmark run. Explicitly
reviewed post-loop observations are also retained where they define a result;
these interfaces are not identical to just the original timed region.

## Plan

### 1. Inventory and contracts

- [x] Inventory all 151 calls from the source's `main`, preserving categories,
      source locations, and hashes.
- [x] Define reviewed interfaces and transformations for an initial 35 1D cases.
- [x] Record every other case as `needs_review`, with a reason; do not omit it or
      manufacture a signature.
- [x] Pin the reviewed source snapshot and refuse unreviewed source changes.

For each generated case, record array access modes and required extents, scalar
arguments/outputs, valid sizes, aliasing, arithmetic semantics, and adaptations.
Use signed 32-bit `int`. Do **not** silently choose wraparound arithmetic, add
`restrict`, or require a multiple of the SIMD width. For this first batch,
arrays occupy separate storage as in the original globals; `const` describes
read-only parameters but is not an aliasing guarantee. Require initialized valid
buffers and defined signed arithmetic for every intermediate expression.

### 2. Generate the first batch

- [x] Emit self-contained `kernels/NAME.c`, `kernels.h`, and `manifest.json` into
      a new directory, separate from `generated/tsvc-int`.
- [x] Strip only recognized harness scaffolding and the outer repetition loop;
      preserve local declarations even if they precede the timing declarations.
- [x] Substitute `LEN`/`lll` with `n`, `TYPE` with `int`, and reviewed integral
      floating literals with integer literals.
- [x] Return scalar reductions explicitly instead of losing them with `dummy`.
- [x] Include contracts in per-case JSON and readable comments on each kernel.

The initial batch is deliberately finite and reviewed, not a general C parser.
Fail on unexpected scaffold layouts rather than silently extracting partial code.

### 3. Validate extraction independently

- [x] Emit test-only reference wrappers retaining the **original complete
      function text** and global-array names. Stub timing/init/check/dummy and
      force the original repetition loop to run once. Bind its `LEN` to the
      requested runtime size. This is not the rewritten kernel used twice.
- [x] Compile reference and extracted implementations in separate translation
      units and compare every array element (including read-only arrays), scalar
      results, and guard regions.
- [x] Test zero/small/odd/tail sizes and reproducible mixed-sign inputs.
- [x] Run AddressSanitizer and UndefinedBehaviorSanitizer; never mask overflow
      with `-fwrapv`.
- [x] Add regression tests for inventory, source changes, contracts, extraction,
      deterministic generation, and deliberately incorrect candidates.

These are extraction/differential tests, **not formal verification**. Small safe
inputs do not prove the contract for all integer values. The original benchmark
harness's generic initialization/check routines are intentionally not the oracle.
Reviewed result expressions and post-loop computations are retained separately.

### 4. Extend to all remaining cases

- [x] Establish 2D support for 19 reviewed cases: logical square dimension `n`,
      shared physical row stride `ld`, and explicit vector/matrix/packed extents.
      Kernels use flat indexing; reference adapters independently retain C's
      two-dimensional indexing with pointer-to-VLA aliases.
- [x] Test compact/padded layouts, padding preservation, transposes, triangular
      partial writes, and contiguous packed outputs. Preserve 1D source/ABI and
      schema-1 checker compatibility; emit layout contracts in schema 2.
- [x] Complete the remaining matrix cases with nontrivial overflow-safe test
      profiles. Retain `s2111`'s post-loop checksum and zero-to-three fallback.
      Give `s258`/`vbor` valid single-row extents instead of cross-row accesses.
- [x] Indirect indexing: expose read-only index arrays with explicit `[0,n)`
      domains, allow duplicate indices, and preserve ordered scatter semantics.
      Cover every `INDIRECT_ADDRESSING` case plus `vag`, `vas`, and `s353`.
- [x] Add offset-vector extents and scalar domains for `s4114`/`s4116`; distinguish
      offsets, 1-based row/start parameters, and matrix leading dimensions.
- [x] Add six reductions, retain prefix-sum arrays as well as returned sums,
      and distinguish observations saved in `temp` from dummy arguments.
- [x] Preserve `s353`'s multiple-of-five constraint and nonempty min/max inputs.
      Report eligible/excluded test sizes; test six index patterns independently
      of data trials. Emit schema 3 and retain schema 1/2 checker compatibility.
- [x] Add product and coupled reductions, integer absolute-value maximum,
      matrix extrema with explicit scalar/index/checksum outputs, and searches
      with preserved no-match sentinels. Do not silently combine differing dummy
      and post-loop observations or change first/last-match tie rules.
- [x] Include four reviewed leaf helpers in self-contained kernels; parameterize
      their size/pointer interfaces, record helper hashes, and reject unreviewed
      calls. Preserve `s31111`'s fixed 32-element footprint, not an invented n-sum.
- [x] Complete packing/unpacking, including conditional column-major matrix
      packing and untouched suffixes. Add `s351`/`s352` with their original
      multiple-of-five restrictions.
- [x] Complete the three `RECURRENCES` cases with nontrivial overflow-safe test
      profiles. Product/recurrence test restrictions are separate from caller
      contracts; test small full-range and larger bounded-coefficient cases.
- [x] Emit schema 4 and test scalar slots, helper calls, integer-limit absolute
      values, and nonzero large products; retain schema 1/2/3 compatibility.
- [x] Add 44 more cases covering ordinary 1D/control flow, symbolic steps/offsets,
      node splitting, pointer induction, and all five equivalencing kernels.
- [x] Model overlapping views with a single caller-provided backing object, not
      disjoint copies. Preserve the true 64-element dependence in `s424`, partial
      writes, initial-view offsets, and advancing pointer semantics in `s1351`.
- [x] Retain six exact post-loop sums as observable returns. Remove only listed
      benchmark initializers; check pointer setup and constants exactly. Include
      the fifth leaf helper, `s471s`, with its original no-op body.
- [x] Add extended, strided, and signed-offset storage contracts; exercise zero
      stride, inactive negative offsets, and independent symbolic start/step values.
- [x] Distinguish `s442`'s arbitrary-integer selectors from bounded gather/scatter
      indices. Test all four branches plus default fallthrough and integer limits.
- [x] Add an overflow-safe repeated-square test profile for `s222` without narrowing
      its caller contract. Test new branch/dependence boundaries at 10/11 and 66/67.
- [x] Emit schema 5; retain schemas 1–4 compatibility. All 92 earlier kernel sources
      and interfaces remain unchanged; the saved v4 dataset passes again.
- [x] Complete `s315`/`s318`: remove only the reviewed pre-timer initializer,
      preserve first-maximum ties, distinguish logical indices from strided
      addresses, and expose maximum/index/checksum plus the original return.
- [x] Review the five fractional-cast cases, retaining literal truncation to zero
      rather than inventing division. Flag their degenerate integer semantics.
- [x] Review `s451`: select double sin/cos with final int truncation, link libm,
      and explicitly mark mixed arithmetic and floating-environment assumptions.
- [x] Review `s481`: return a stop index (or -1), preserving prefix writes and
      stopping before the failing element's update; do not exit the process.
- [x] Review remaining dependencies: standard libm is explicit; no additional
      unreviewed TSVC helper calls remain.
- [x] Preserve fixed bounds, divisibility, and minimum sizes. Add the isolated
      excluded size `s292 n=1` without discarding its valid empty behavior.
- [x] Emit schema 6 with semantic caveats and single-row extents; retain checker
      compatibility with schemas 1–5 and all earlier kernel/reference sources.
- [x] Bring every case through compilation/sanitizer/differential checks.

All 151 now have reviewed contracts and generated kernels, not placeholders.
This completes dataset construction under the documented adaptation policy,
not formal validation or equivalence to the floating-point originals.

Current validation: 90 regression tests, 144,072 default sanitized differential
executions, and 14,544 additional executions for the final 15 (vectors through
4096, matrices through 128). The saved v5 dataset passes its 129,960 executions
again; all 136 earlier kernel/reference files and signatures are unchanged.

### 5. Integrate the experiment workflow (subsequent work)

- [ ] Define performance/verification cohorts using the explicit semantic caveats;
      do not silently pool degenerate, mixed-libm, termination, and extent-adapted
      cases into ordinary integer results.
- [ ] Feed only kernel + contract to the LLM; keep harness/reference out of prompts.
- [ ] Compile candidates and use the same full-state differential tests.
- [ ] Add compatible Clang/Alive2 IR generation and explicit validation assumptions.
- [ ] Keep test-plausible, bounded-validated, refuted, and inconclusive separate.
- [ ] Benchmark on the AVX2 execution host with initialization/repetition outside
      the measured kernel. Record toolchain, model, seeds, and dataset hashes.
