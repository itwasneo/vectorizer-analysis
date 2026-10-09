# vectorizer-analysis

Reimplementing the LLM-Vectorizer workflow on TSVC benchmarks.

## Parameterized integer kernels

- [Implementation plan](docs/tsvc-parameterization-plan.md)
- [Generation, contracts, and testing](docs/tsvc-kernels.md)
- [Final-case semantic adaptations and reporting policy](docs/tsvc-final-adaptations.md)

### Run on the testing machine

The frozen dataset is included in Git: `generated/tsvc-kernels-v6/` contains all
151 kernels, references, contracts, the header, manifest, and upstream license.
After pulling this repository, use Python 3.10+ and Clang with ASan/UBSan and libm:

```sh
python3 scripts/check_tsvc_kernels.py --directory generated/tsvc-kernels-v6 --sanitize \
  --report generated/tsvc-kernels-v6/validation-report.json
```

No TSVC checkout, regeneration, or LLM is needed for this check. Reports are local
and ignored by Git. Regeneration and the full Python regression suite **do** need
the pinned upstream TSVC checkout; see [setup instructions](docs/tsvc-kernels.md#regenerate-or-run-generator-regression-tests).
Do not regenerate into the committed snapshot: use a new/empty output directory.

All **151** benchmarks now have reviewed parameterized implementations: **122 1D,
27 square-matrix, and 2 single-row cases**, across all 18 categories. Support includes
matrix strides, repeated indirect indices, helpers, explicit scalar/index outputs,
packing, and shared-storage pointer views.

These are **documented adaptations, not just unchanged functions in wrappers**.
Five fractional-cast cases become numerically degenerate; `s451` retains double
libm arithmetic with integer storage; `s481` returns a stop index instead of
exiting the process. Two first-row accesses have an explicit valid-row storage
contract. These cases are flagged for separate experimental reporting.

Validation: **90 regression tests**, **144,072** default sanitized differential
executions, and **14,544** larger-input executions for the final 15 cases. These
are test results, not Alive2 verification or equivalence to floating-point TSVC.

Only the frozen v6 dataset is versioned. The earlier 35-, 54-, 71-, 92-, and
136-case datasets remain preserved locally but are not included in Git, nor are
machine-specific validation reports. All 136 prior kernel and reference sources
remain byte-identical in v6. The earlier whole-program integer extractor
(`scripts/extract_tsvc_int.py`) remains available separately.
