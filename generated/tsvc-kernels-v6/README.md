# Parameterized integer TSVC kernels

151 kernels are emitted; all 151 benchmark cases appear in `manifest.json`.
Cases marked `needs_review` are not silently dropped or claimed as supported.
See `docs/tsvc-parameterization-plan.md` and `docs/tsvc-kernels.md` in the project.

- `kernels/`: self-contained C11 functions, no main or mutable global state.
- `contracts/`: per-case interface, bounds, assumptions, and source provenance.
- `kernels.h`: declarations for the generated interfaces.
- `reference/`: test-only adapters around original TSVC functions, not LLM inputs.
- `LICENSE.TXT`: upstream TSVC license; applies to copied/adapted source.

The kernel performs one computational repetition. It is an integer adaptation,
not equivalent to the original floating-point benchmark. It is not the paper's
149-function dataset. Generation is not testing or formal validation.
Reviewed post-loop observations are part of the kernel interface where listed.
Five fractional-cast cases are numerically degenerate. s451 uses integer storage
but double libm arithmetic; s481 returns a stop outcome instead of exiting the
process. s258/vbor require a valid single row rather than an out-of-row access.
These cases have explicit experiment_caveats and must be reported separately.

From the project root, run:

    python3 scripts/check_tsvc_kernels.py --directory /path/to/this/dataset --sanitize

The original whole-program files in `generated/tsvc-int` are unrelated outputs
and are not used as the testing oracle. In particular, their initializers and
checksums are not suitable as a correctness oracle for this adaptation.
