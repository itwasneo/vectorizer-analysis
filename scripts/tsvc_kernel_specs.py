"""Reviewed interfaces for the parameterized TSVC batches.

Adding a case requires inspecting its computation, bounds, and outputs, not just
adding its name. The source hash is a safety gate for this snapshot-specific
extractor; update it only after reviewing upstream changes.
"""

from dataclasses import dataclass

REVIEWED_SOURCE_SHA256 = "4a90a9a5470e635d5a3bcffe53816ce1b1ef2cefe15782567debe8f727908ecb"

# These are caller preconditions, not runtime checks or implicit assumptions.
SCALAR_DOMAINS = {
    "start_1based": {"minimum": "1", "maximum": "n+1"},
    "matrix_row_1based": {"minimum": "1", "maximum": "max(1,n)"},
    "nonnegative_offset": {"minimum": "0", "maximum": "INT_MAX-n"},
    "positive_step": {"minimum": "1", "maximum": "INT_MAX-n"},
    "signed_offset": {"minimum": "INT_MIN", "maximum": "INT_MAX-n"},
    "nonnegative_stride": {"minimum": "0", "maximum": "INT_MAX/max(1,n)"},
    "half_length": {"minimum": "0", "maximum": "n/2"},
}


@dataclass(frozen=True)
class HelperSpec:
    source_signature: str
    parameters: tuple[str, ...]
    array_arguments: tuple[int, ...] = ()
    needs_n: bool = False


# Reviewed leaf helpers. Bodies are read from the pinned source, not recreated
# from the kernels. Array parameters decay to pointers without evaluating a
# potentially zero VLA bound; const qualifies only reviewed read-only arguments.
HELPERS = {
    "s151s": HelperSpec("int s151s(TYPE a[LEN], TYPE b[LEN], int m)",
                        ("int *a", "const int *b", "int m"), (0, 1), True),
    "s152s": HelperSpec("int s152s(TYPE a[LEN], TYPE b[LEN], TYPE c[LEN], int i)",
                        ("int *a", "const int *b", "const int *c", "int i"), (0, 1, 2)),
    "test": HelperSpec("TYPE test(TYPE* A)", ("const int *A",), (0,)),
    "f": HelperSpec("static inline TYPE f(TYPE a, TYPE b)", ("int a", "int b")),
    "s471s": HelperSpec("static inline int s471s(void)", ()),
}
TEST_PROFILES = {
    "default": "Data in [-3,3]; zero, one, minus-one, alternating, and seeded random trials.",
    "bounded_product": "At most 18 factors have magnitude 2 or 3; all others are -1, 0, or 1. Every prefix product has magnitude at most 3^18.",
    "first_order_recurrence": "Full [-3,3] coefficients for n<=8; otherwise b is in [-1,1], so |a[i]| <= 3*(i+1).",
    "second_order_recurrence": "Full [-3,3] coefficients for n<=8; otherwise each (b[i],c[i]) has at most one nonzero entry in {-1,1}, so |a[i]| <= 3*(i+1).",
    "repeated_square": "Full [-3,3] inputs for n<=5 (largest square chain ends at 3^16); for larger n only e[0] is clamped to {-1,0,1}.",
    "triangular_recurrence": "Full [-3,3] coefficients for n<=8; otherwise at most one unit-magnitude coefficient per active matrix column. This bounds |a[i]| by 3*(i+1).",
    "triangular_squares": "Full [-3,3] inputs for n<=5; otherwise construct bb from independent bounded target values so each updated aa value stays in [-3,3]. Initial aa and padding are preserved during preparation.",
    "wavefront": "Full [-3,3] inputs for n<=8; otherwise set only row/column boundaries to a bounded six-period wave f(i-j), with f(k)=f(k-1)+f(k+1). Interior inputs remain independently initialized.",
    "bounded_vbor": "Logical input values in [-2,2], including uniform +/-2 trials. Each x has magnitude <=737280; at the tester's n<=128, every checksum prefix has magnitude <=94371840. Padding is not clamped.",
    "integer_trig": "Integer-storage inputs include [-3,3], +/-1000, INT_MIN, and INT_MAX; libm receives exact binary64 conversions and the sum is truncated to int.",
    "termination": "Exercise no stop and first/middle/last stop positions independently of data trials; use mixed-sign data before and after the stop.",
}


@dataclass(frozen=True)
class PointerView:
    name: str
    base: str
    offset: str
    binding: str
    access: str = "read"
    declaration: bool = False


@dataclass(frozen=True)
class KernelSpec:
    read: str = ""
    write: str = ""
    update: str = ""
    scalars: tuple[str, ...] = ()
    result: str | None = None
    note: str = ""
    matrices: str = ""
    flat_square: str = ""
    pointer_params: tuple[str, ...] = ()
    index_arrays: str = ""
    scalar_domains: tuple[tuple[str, str], ...] = ()
    offset_vectors: tuple[tuple[str, str], ...] = ()
    minimum_n: int = 0
    n_multiple: int = 1
    start_clock_calls: int = 1
    result_source: str = "dummy"
    result_expression: str | None = None
    dummy_result: str | None = None
    outputs: tuple[str, ...] = ()
    helpers: tuple[str, ...] = ()
    integer_abs: bool = False
    exclude_int_min: str = ""
    test_profile: str = "default"
    empty_input: str | None = None
    views: tuple[PointerView, ...] = ()
    extra_elements: tuple[tuple[str, int], ...] = ()
    strided_vectors: tuple[tuple[str, str], ...] = ()
    clamped_offsets: str = ""
    selector_arrays: str = ""
    remove_initializers: tuple[str, ...] = ()
    postlude: str | None = None
    constants: tuple[tuple[str, int], ...] = ()
    single_row_matrix: bool = False
    excluded_n: tuple[int, ...] = ()
    fractional_casts: tuple[str, ...] = ()
    double_trig: bool = False
    termination: bool = False

    def __post_init__(self) -> None:
        matrices, flat = set(self.matrices.split()), set(self.flat_square.split())
        if (matrices | flat) - self.arrays.keys() or matrices & flat:
            raise ValueError("invalid array layout specification")
        if flat and not matrices:
            raise ValueError("flat-square storage requires a reviewed matrix case")
        if self.single_row_matrix and (not matrices or flat):
            raise ValueError("single-row storage requires matrices without square-packed buffers")
        if len(set(self.excluded_n)) != len(self.excluded_n) or any(n < self.minimum_n for n in self.excluded_n):
            raise ValueError("invalid excluded sizes")
        if (len(set(self.fractional_casts)) != len(self.fractional_casts)
                or set(self.fractional_casts) - {".5", ".333", ".99"}):
            raise ValueError("unreviewed fractional cast")
        indices = set(self.index_arrays.split())
        if indices - self.arrays.keys() or any(self.arrays[key] != "read" for key in indices):
            raise ValueError("index arrays must be reviewed read-only inputs")
        if set(self.pointer_params) - indices:
            raise ValueError("only reviewed index pointers are supported as original pointer parameters")
        domains = dict(self.scalar_domains)
        if (len(domains) != len(self.scalar_domains) or domains.keys() - set(self.scalars)
                or set(domains.values()) - SCALAR_DOMAINS.keys()):
            raise ValueError("invalid scalar domains")
        offsets = dict(self.offset_vectors)
        if (len(offsets) != len(self.offset_vectors) or offsets.keys() - self.arrays.keys()
                or offsets.keys() & (matrices | flat | indices)
                or any(domains.get(value) not in ("nonnegative_offset", "positive_step", "signed_offset") for value in offsets.values())):
            raise ValueError("invalid offset-vector extents")
        clamped = set(self.clamped_offsets.split())
        if clamped != {key for key, value in offsets.items() if domains[value] == "signed_offset"}:
            raise ValueError("signed offsets must be clamped in the allocation extent")
        extra, strides = dict(self.extra_elements), dict(self.strided_vectors)
        if (len(extra) != len(self.extra_elements) or len(strides) != len(self.strided_vectors)
                or (extra.keys() | strides.keys()) - self.arrays.keys()
                or extra.keys() & strides.keys()
                or (extra.keys() | strides.keys()) & (matrices | flat | indices | offsets.keys())
                or any(value < 1 for value in extra.values())
                or any(domains.get(value) != "nonnegative_stride" for value in strides.values())):
            raise ValueError("invalid extended/strided vector extents")
        selectors = set(self.selector_arrays.split())
        if (selectors - self.arrays.keys() or indices & selectors
                or any(self.arrays[key] != "read" for key in selectors)):
            raise ValueError("selectors must be distinct read-only buffers")
        view_names = {view.name for view in self.views}
        if (len(view_names) != len(self.views) or view_names & (self.arrays.keys() | set(self.scalars))
                or any(view.base not in self.arrays or view.access not in ("read", "write", "read_write")
                       or (view.access != "read" and self.arrays[view.base] == "read") for view in self.views)):
            raise ValueError("invalid derived pointer views")
        if self.minimum_n < 0 or self.n_multiple < 1 or self.start_clock_calls not in (1, 2):
            raise ValueError("invalid size or scaffold recipe")
        if self.result_source not in ("dummy", "temp", "postlude", "termination") or (self.result_source != "dummy" and not self.result):
            raise ValueError("invalid scalar observation")
        if self.termination != (self.result_source == "termination") or (self.termination and (self.result != "stop_index" or self.outputs)):
            raise ValueError("termination requires a dedicated stop-index return")
        if bool(self.postlude) != (self.result_source == "postlude"):
            raise ValueError("post-loop computation requires a reviewed postlude observation")
        if self.result_expression and (not self.result or self.result_source != "temp"):
            raise ValueError("post-loop expressions require a temp observation")
        if self.dummy_result and self.dummy_result not in self.outputs:
            raise ValueError("a differing dummy observation must be exposed explicitly")
        if (len(set(self.outputs)) != len(self.outputs)
                or {f"out_{key}" for key in self.outputs} & (self.arrays.keys() | set(self.scalars) | {"n", "ld"})):
            raise ValueError("invalid scalar output parameters")
        if set(self.helpers) - HELPERS.keys() or len(set(self.helpers)) != len(self.helpers):
            raise ValueError("unreviewed or duplicate helpers")
        if set(self.exclude_int_min.split()) - self.arrays.keys():
            raise ValueError("unknown INT_MIN-excluded arrays")
        if self.integer_abs and not self.exclude_int_min:
            raise ValueError("integer absolute value needs an explicit INT_MIN exclusion")
        if self.test_profile not in TEST_PROFILES:
            raise ValueError("unreviewed test-input profile")

    @property
    def return_expression(self) -> str | None:
        return "-1" if self.termination else self.result_expression or self.result

    def layout(self, name: str) -> str:
        if name in self.matrices.split():
            return "row_major_matrix"
        if name in self.flat_square.split():
            return "flat_square"
        if name in dict(self.offset_vectors):
            return "offset_vector"
        if name in dict(self.extra_elements):
            return "extended_vector"
        if name in dict(self.strided_vectors):
            return "strided_vector"
        return "vector"

    @property
    def arrays(self) -> dict[str, str]:
        modes = {}
        for names, mode in ((self.read, "read"), (self.write, "write"),
                            (self.update, "read_write")):
            for name in names.split():
                if name in modes:
                    raise ValueError(f"duplicate array: {name}")
                modes[name] = mode
        return dict(sorted(modes.items()))

    @property
    def return_type(self) -> str:
        return "int" if self.result else "void"


SPECS = {
    "s000": KernelSpec(read="Y", write="X"),
    "s111": KernelSpec(read="b", update="a", note="Only odd indices are updated."),
    "s1111": KernelSpec(read="b c d", write="a", note="Runs floor(n/2) iterations; other elements are preserved."),
    "s112": KernelSpec(read="b", update="a", note="Reverse traversal; retain the n-2 initial index."),
    "s1112": KernelSpec(read="b", write="a"),
    "s113": KernelSpec(read="b", update="a"),
    "s1113": KernelSpec(read="b", update="a", note="The a[n/2] dependence is preserved, not hoisted."),
    "s116": KernelSpec(update="a", note="Preserve the original i < n-5 bound and step of five, including untouched tails."),
    "s121": KernelSpec(read="b", update="a", note="Reads a[i+1]; the bound remains n-1."),
    "s123": KernelSpec(read="b c d e", write="a", note="Data-dependent output prefix of at most 2*floor(n/2) elements; preserve the rest."),
    "s124": KernelSpec(read="b c d e", write="a"),
    "s127": KernelSpec(read="b c d e", write="a", note="Writes 2*floor(n/2) elements; an odd final element is preserved."),
    "s211": KernelSpec(read="c d e", write="a", update="b"),
    "s212": KernelSpec(read="c d", update="a b"),
    "s1213": KernelSpec(read="c d", update="a b"),
    "s221": KernelSpec(read="c d", update="a b"),
    "s1221": KernelSpec(read="a", update="b"),
    "s271": KernelSpec(read="b c", update="a"),
    "s272": KernelSpec(read="c d e", update="a b", scalars=("t",)),
    "s273": KernelSpec(read="d e", update="a b c"),
    "s274": KernelSpec(read="c d e", write="a", update="b"),
    "s276": KernelSpec(read="b c d", update="a"),
    "s277": KernelSpec(read="c d e", update="a b"),
    "s278": KernelSpec(read="d e", update="a b c"),
    "s279": KernelSpec(read="d e", update="a b c"),
    "s453": KernelSpec(read="b", write="a", note="Retain local s=0 and the scalar recurrence s+=2; it is not an input."),
    "vif": KernelSpec(read="b", write="a"),
    "vpv": KernelSpec(read="b", update="a"),
    "vtv": KernelSpec(read="b", update="a"),
    "vpvtv": KernelSpec(read="b c", update="a"),
    "vpvts": KernelSpec(read="b", update="a", scalars=("s",)),
    "vpvpv": KernelSpec(read="b c", update="a"),
    "vtvtv": KernelSpec(read="b c", update="a"),
    "vsumr": KernelSpec(read="a", result="sum", note="Expose the reduction passed to dummy as the return value; return 0 for n=0."),
    "vdotr": KernelSpec(read="a b", result="dot", result_source="temp", note="Expose the dot product as the return value; return 0 for n=0."),
    # Square LEN2 computations: n is the logical side, ld is a shared physical
    # row stride. 'array' remains contiguous n*n storage, independent of ld.
    "s114": KernelSpec(read="bb", update="aa", matrices="aa bb",
                       note="Preserve the triangular domain and transposed read aa[j][i]."),
    "s1115": KernelSpec(read="bb cc", update="aa", matrices="aa bb cc"),
    "s119": KernelSpec(read="bb", update="aa", matrices="aa bb"),
    "s1119": KernelSpec(read="bb", update="aa", matrices="aa bb"),
    "s125": KernelSpec(read="aa bb cc", write="array", matrices="aa bb cc", flat_square="array",
                       note="Pack the n*n results contiguously in row-major iteration order; array has no row padding."),
    "s126": KernelSpec(read="array cc", update="bb", matrices="bb cc", flat_square="array",
                       note="Preserve k increments and skipped entries of the contiguous array; k ends at n*n+1."),
    "s132": KernelSpec(read="b c", update="aa", matrices="aa",
                       note="Rows 0 and 1 and c[1] are accessed only when n>=2; n=0 and n=1 perform no writes."),
    "s141": KernelSpec(read="bb", update="array", matrices="bb", flat_square="array",
                       note="Packed triangular index i+j*(j+1)/2; retain the original k recurrence. Conservatively provide n*n array elements and preserve the unused suffix."),
    "s231": KernelSpec(read="bb", update="aa", matrices="aa bb"),
    "s1232": KernelSpec(read="bb cc", write="aa", matrices="aa bb cc"),
    "s233": KernelSpec(read="cc", update="aa bb", matrices="aa bb cc"),
    "s2233": KernelSpec(read="cc", update="aa bb", matrices="aa bb cc"),
    "s235": KernelSpec(read="b c bb", update="a aa", matrices="aa bb"),
    "s256": KernelSpec(read="bb d", write="cc", update="a", matrices="bb cc"),
    "s257": KernelSpec(read="bb", update="a aa", matrices="aa bb"),
    "s275": KernelSpec(read="bb cc", update="aa", matrices="aa bb cc"),
    "s2275": KernelSpec(read="b c d bb cc", write="a", update="aa", matrices="aa bb cc"),
    "s2101": KernelSpec(read="bb cc", update="aa", matrices="aa bb cc"),
    "s2102": KernelSpec(write="aa", matrices="aa",
                        note="Set only the logical n*n matrix to identity; leave row padding unchanged."),
    # Index arrays are not necessarily permutations. Repeated scatter addresses
    # retain sequential/last-store semantics; no injectivity assumption is added.
    "s491": KernelSpec(read="b c d ip", write="a", pointer_params=("ip",), index_arrays="ip",
                       note="Duplicate destinations are allowed; the last scalar store to each destination wins."),
    "s4112": KernelSpec(read="b ip", update="a", scalars=("s",), pointer_params=("ip",), index_arrays="ip"),
    "s4113": KernelSpec(read="b c ip", write="a", pointer_params=("ip",), index_arrays="ip",
                        note="Repeated destinations preserve the order-dependent last store, including the c[i] term."),
    "s4114": KernelSpec(read="b c d ip", write="a", scalars=("n1",), pointer_params=("ip",), index_arrays="ip",
                        scalar_domains=(("n1", "start_1based"),),
                        note="n1 is a 1-based start; n1=n+1 selects an empty loop. Preserve the reversed c[n-ip[i]-1] access."),
    "s4115": KernelSpec(read="a b ip", result="sum", result_source="temp", pointer_params=("ip",), index_arrays="ip",
                        note="Return the sparse dot product stored in temp, not dummy's constant zero argument."),
    "s4116": KernelSpec(read="a aa ip", matrices="aa", scalars=("j", "inc"), pointer_params=("ip",), index_arrays="ip",
                        scalar_domains=(("j", "matrix_row_1based"), ("inc", "nonnegative_offset")),
                        offset_vectors=(("a", "inc"),), result="sum", result_source="temp",
                        note="j is a 1-based matrix row; inc is a nonnegative offset, not a stride. Provide max(1,n+inc) a elements. Only n-1 terms are summed; n<=1 returns zero."),
    "s4117": KernelSpec(read="b c d", write="a"),
    "va": KernelSpec(read="b", write="a"),
    "vag": KernelSpec(read="b ip", write="a", pointer_params=("ip",), index_arrays="ip"),
    "vas": KernelSpec(read="b ip", write="a", pointer_params=("ip",), index_arrays="ip",
                      note="Duplicate destinations are allowed; preserve last-store semantics and untouched elements."),
    "s353": KernelSpec(read="b c ip", update="a", pointer_params=("ip",), index_arrays="ip",
                       n_multiple=5, start_clock_calls=2,
                       note="The original loop is explicitly unrolled by five, without a tail. Preserve n%5==0 and alpha=c[0]; even n=0 requires a valid initialized c[0]."),
    "s311": KernelSpec(read="a", result="sum"),
    "s313": KernelSpec(read="a b", result="dot", result_source="temp"),
    "s3111": KernelSpec(read="a", result="sum", result_source="temp"),
    "s3112": KernelSpec(read="a", write="b", result="sum", result_source="temp",
                        note="Expose both the complete prefix-sum array b and the final sum; neither output may be dropped."),
    "s314": KernelSpec(read="a", result="x", result_source="temp", minimum_n=1,
                       note="Maximum initialized from a[0]; require nonempty input instead of inventing an empty identity."),
    "s316": KernelSpec(read="a", result="x", result_source="temp", minimum_n=1,
                       note="Minimum initialized from a[0]; require nonempty input instead of inventing an empty identity."),
    # Leaf helper calls preserve the original computation/call structure.
    "s151": KernelSpec(read="b", update="a", helpers=("s151s",)),
    "s152": KernelSpec(read="c d e", write="b", update="a", helpers=("s152s",)),
    "s31111": KernelSpec(read="a", result="sum", helpers=("test",), minimum_n=32,
                         note="Exactly eight four-element helper calls read a[0..31], independent of n. Require n>=32; preserve the unused suffix."),
    "s4121": KernelSpec(read="b c", update="a", helpers=("f",)),
    "s312": KernelSpec(read="a", result="prod", result_source="temp", test_profile="bounded_product",
                       empty_input="No array writes; the empty product returns 1.",
                       note="All evaluated prefix products must fit signed int. The bounded-factor test profile is not a restriction on valid caller inputs."),
    "s319": KernelSpec(read="c d e", write="a b", result="sum", result_source="temp"),
    "s3113": KernelSpec(read="a", result="max", result_source="temp", minimum_n=1,
                        integer_abs=True, exclude_int_min="a",
                        note="Integer absolute-value maximum; exclude INT_MIN, whose positive magnitude is not representable as int."),
    "s3110": KernelSpec(read="aa", matrices="aa", minimum_n=1, result="max", result_source="temp",
                        result_expression="max + xindex+1 + yindex+1", dummy_result="chksum",
                        outputs=("max", "xindex", "yindex", "chksum"),
                        note="Preserve first row-major maximum on ties. Return the original temp expression; expose maximum, zero-based coordinates, and the distinct dummy checksum separately."),
    "s13110": KernelSpec(read="aa", matrices="aa", minimum_n=1, result="max", result_source="temp",
                         result_expression="max + xindex+1 + yindex+1", dummy_result="chksum",
                         outputs=("max", "xindex", "yindex", "chksum"),
                         note="Unlike s3110, xindex and yindex stay zero even if a later maximum is found. Retain both dummy checksum and temp observation."),
    "s331": KernelSpec(read="a", result="j", result_source="temp", result_expression="j+1",
                       dummy_result="chksum", outputs=("j", "chksum"),
                       empty_input="No array writes; return 0, with out_j=out_chksum=-1.",
                       note="Last negative element, not first. Return the original 1-based temp observation; expose the zero-based index (-1 if absent) and dummy checksum."),
    "s332": KernelSpec(read="a", scalars=("t",), result="value", result_source="temp",
                       dummy_result="chksum", outputs=("index", "chksum"),
                       empty_input="No array writes; return -1, with out_index=-2 and out_chksum=-3.",
                       note="First value strictly greater than t. Preserve no-match value=-1, index=-2, and checksum=-3, including for n=0."),
    "s341": KernelSpec(read="b", write="a", start_clock_calls=2,
                       note="Pack positive b values in order; preserve the unused output suffix."),
    "s342": KernelSpec(read="b", update="a", start_clock_calls=2),
    "s343": KernelSpec(read="aa bb", write="array", matrices="aa bb", flat_square="array", start_clock_calls=2,
                       note="Conditional column-major packing (i outer, j inner, aa[j][i]); preserve the unused contiguous output suffix and matrix padding."),
    "s351": KernelSpec(read="b c", update="a", n_multiple=5, start_clock_calls=2,
                       note="Original five-way unrolling has no tail. alpha=c[0] is evaluated even at n=0."),
    "s352": KernelSpec(read="a b", result="dot", result_source="temp", n_multiple=5, start_clock_calls=2),
    "s321": KernelSpec(read="b", update="a", test_profile="first_order_recurrence"),
    "s322": KernelSpec(read="b c", update="a", test_profile="second_order_recurrence"),
    "s323": KernelSpec(read="c d e", update="a b"),
    "s452": KernelSpec(read="b c", write="a"),
    "s482": KernelSpec(read="b c", update="a", note="Perform the update before testing the early-exit condition; preserve all later elements."),
    # Remaining integral 1D computations; preserve ordering and partial writes.
    "s128": KernelSpec(read="c d", write="a", update="b"),
    "s131": KernelSpec(read="b", update="a"),
    "s161": KernelSpec(read="b d e", update="a c"),
    "s1161": KernelSpec(read="c d e", write="b", update="a"),
    "s1279": KernelSpec(read="a b d e", update="c"),
    "s2710": KernelSpec(read="d e", update="a b c", scalars=("x",),
                        note="Preserve both the n>10 branch and the independent sign test on scalar x."),
    "s2711": KernelSpec(read="b c", update="a"),
    "s2712": KernelSpec(read="b c", update="a"),
    "s441": KernelSpec(read="b c d", update="a"),
    "s442": KernelSpec(read="b c d e indx", update="a", selector_arrays="indx",
                       note="Selectors are arbitrary signed ints, not bounded addresses. Values other than 1,2,3,4 fall through to L15 (the case-1 computation)."),
    "s443": KernelSpec(read="b c d", update="a"),
    "s173": KernelSpec(read="b", update="a"),
    "s176": KernelSpec(read="b c", update="a", note="Keep both convolution loops; preserve a[floor(n/2)..n)."),
    "s241": KernelSpec(read="c d", update="a b"),
    "s242": KernelSpec(read="b c d", update="a", scalars=("s1", "s2")),
    "s243": KernelSpec(read="c d e", update="a b"),
    "s244": KernelSpec(read="c d", update="a b"),
    "s1244": KernelSpec(read="b c", write="d", update="a"),
    "s2244": KernelSpec(read="b c e", write="a"),
    "s251": KernelSpec(read="b c d", write="a"),
    "s1251": KernelSpec(read="c d e", update="a b"),
    "s2251": KernelSpec(read="c d e", write="a", update="b"),
    "s3251": KernelSpec(read="c e", write="d", update="a b"),
    "s252": KernelSpec(read="b c", write="a"),
    "s253": KernelSpec(read="b d", update="a c"),
    "s261": KernelSpec(read="b d", update="a c"),
    "s281": KernelSpec(read="c", update="a b", note="Reversed a reads can observe earlier writes after crossing the midpoint; do not snapshot a."),
    "s1281": KernelSpec(read="c d e", update="a b"),
    "s293": KernelSpec(update="a"),
    "s431": KernelSpec(read="b", update="a"),
    "s122": KernelSpec(read="b", update="a", scalars=("n1", "n3"),
                       scalar_domains=(("n1", "start_1based"), ("n3", "positive_step")),
                       note="Positive step bounds the final induction increment; n1=n+1 is empty. b is traversed backwards once per executed iteration, not once per source index."),
    "s172": KernelSpec(read="b", update="a", scalars=("n1", "n3"),
                       scalar_domains=(("n1", "start_1based"), ("n3", "positive_step"))),
    "s174": KernelSpec(read="b", update="a", scalars=("M",), scalar_domains=(("M", "half_length"),)),
    "s162": KernelSpec(read="b c", update="a", scalars=("k",),
                       scalar_domains=(("k", "signed_offset"),), offset_vectors=(("a", "k"),), clamped_offsets="a",
                       note="k<=0 does no work. Positive k needs max(1,n+max(0,k)) initialized a elements; k is an offset, not a loop stride."),
    "s171": KernelSpec(read="b", update="a", scalars=("inc",),
                       scalar_domains=(("inc", "nonnegative_stride"),), strided_vectors=(("a", "inc"),),
                       note="inc=0 repeatedly accumulates into a[0]. Provide max(1,n*inc) a elements, including all preserved stride gaps."),
    "s175": KernelSpec(read="b", update="a", scalars=("inc",),
                       scalar_domains=(("inc", "positive_step"),), offset_vectors=(("a", "inc"),),
                       note="The final a[i+inc] read may be past logical n; provide max(1,n+inc) elements. inc must be positive and the final increment must fit int."),
    "s222": KernelSpec(read="b c", update="a e", test_profile="repeated_square"),
    "s1351": KernelSpec(read="b c", write="a", start_clock_calls=2,
                        views=(PointerView("A", "a", "0", "TYPE* __restrict__ A = a;", "write", True),
                               PointerView("B", "b", "0", "TYPE* __restrict__ B = b;", "read", True),
                               PointerView("C", "c", "0", "TYPE* __restrict__ C = c;", "read", True)),
                        note="Local pointers advance together through separate buffers. Remove original local restrict qualifiers; retain pointer induction, including one-past end pointers."),
    # Each derived view shares the caller's backing buffer, never a copied or
    # disjoint extra input. Only reviewed benchmark initializers are removed.
    "s421": KernelSpec(read="a", update="xx", views=(PointerView("yy", "xx", "0", "yy = xx;"),),
                       remove_initializers=("set1d(xx, 1., 1);",), result="checksum", result_source="postlude",
                       postlude="temp = 0; for (int i = 0; i < LEN; i++){ temp += xx[i]; }"),
    "s1421": KernelSpec(read="a", update="b", views=(PointerView("xx", "b", "n/2", "xx = &b[LEN/2];"),),
                        remove_initializers=("set1d(xx, 1., 1);",), result="checksum", result_source="postlude",
                        postlude="temp = 0; for (int i = 0; i < LEN/2; i++){ temp += xx[i]; }",
                        note="The removed set1d initializes unrelated old xx storage before rebinding. Read the upper half of b and write the lower half; return the original upper-half sum."),
    "s422": KernelSpec(read="a", update="array", extra_elements=(("array", 8),),
                       views=(PointerView("xx", "array", "4", "xx = array + 4;", "read_write"),),
                       remove_initializers=("set1d(xx, 0., 1);",), result="checksum", result_source="postlude",
                       postlude="temp = 0; for (int i = 0; i < LEN; i++){ temp += xx[i]; }"),
    "s423": KernelSpec(read="a", update="array", extra_elements=(("array", 64),), constants=(("vl", 64),),
                       views=(PointerView("xx", "array", "64", "xx = array+vl;"),),
                       remove_initializers=("set1d(xx, 1., 1);",), result="checksum", result_source="postlude",
                       postlude="temp = 0.; for (int i = 0; i < LEN; i++){ temp += array[i]; }"),
    "s424": KernelSpec(read="a", update="array", extra_elements=(("array", 63),), constants=(("vl", 63),),
                       views=(PointerView("xx", "array", "63", "xx = array + vl;", "read_write"),),
                       remove_initializers=("set1d(xx, 0., 1);",), result="checksum", result_source="postlude",
                       postlude="temp = 0.; for (int i = 0; i < LEN; i++){ temp += xx[i]; }",
                       note="Preserve the true 64-element recurrence between array[i] reads and xx[i+1] writes. The post-loop sum includes xx[0], which the computational loop does not overwrite."),
    "s471": KernelSpec(read="c d e", write="x", update="b", helpers=("s471s",),
                       remove_initializers=("set1d(x, 0., 1);",), result="checksum", result_source="postlude",
                       postlude="temp = 0.; for (int i = 0; i < LEN; i++){ temp += x[i]; }"),
    # Final reviewed cases. Numeric/control deviations are recorded separately
    # from kernelization; in particular fractional casts are intentionally zero.
    "s115": KernelSpec(read="aa", update="a", matrices="aa", test_profile="triangular_recurrence"),
    "s118": KernelSpec(read="bb", update="a", matrices="bb", test_profile="triangular_recurrence"),
    "s232": KernelSpec(read="bb", update="aa", matrices="aa bb", test_profile="triangular_squares"),
    "s2111": KernelSpec(update="aa", matrices="aa", test_profile="wavefront", result="checksum", result_source="postlude",
                        postlude="temp = 0.; for (int i = 0; i < LEN2; i++) for (int j = 0; j < LEN2; j++) temp += aa[i][j]; if (temp == 0) temp = 3.;",
                        empty_input="No array writes; the original zero-checksum fallback returns 3, including n=0.",
                        note="Retain the post-loop sum and its zero-to-three fallback, not just the wavefront writes."),
    "s258": KernelSpec(read="a c d aa", write="b e", matrices="aa", single_row_matrix=True,
                       note="aa is one valid row of n columns, not an n*n matrix or a cross-row memory walk. Preserve the carried s across iterations where a[i]<=0."),
    "vbor": KernelSpec(read="a b c d e aa", write="x", matrices="aa", single_row_matrix=True,
                       result="checksum", result_source="postlude", test_profile="bounded_vbor",
                       postlude="temp = 0.; for (int i = 0; i < LEN; i++){ temp += x[i]; }",
                       note="One valid aa row of n columns. Retain all original staged products and the post-loop sum; every product and checksum prefix must fit int."),
    "s254": KernelSpec(read="b", write="a", minimum_n=1, fractional_casts=(".5",),
                       note="The explicit integer cast of .5 is zero, not division by two. Keep the evaluated sum and carry setup; b[n-1] excludes empty input."),
    "s255": KernelSpec(read="b", write="a", minimum_n=2, fractional_casts=(".333",),
                       note="The explicit integer cast of .333 is zero, not division by three. Both evaluated additions must fit; the two-element carry setup needs n>=2."),
    "s291": KernelSpec(read="b", write="a", fractional_casts=(".5",),
                       note="The cast of .5 is zero. Preserve wraparound indices and evaluated sums; n=0 has no array access."),
    "s292": KernelSpec(read="b", write="a", fractional_casts=(".333",), excluded_n=(1,),
                       note="The cast of .333 is zero. n=0 is valid and unchanged; n=1 is excluded because the first b[im2] would have index -1."),
    "s317": KernelSpec(result="q", result_source="temp", fractional_casts=(".99",),
                       empty_input="No arrays; return 1 for n=0 or n=1, otherwise 0.",
                       note="The cast of .99 is zero. Retain the n/2-trip product loop, but classify its integer behavior as degenerate, not floating-point decay."),
    "s315": KernelSpec(read="a", minimum_n=1, result="x", result_source="temp", result_expression="index+x+1",
                       dummy_result="chksum", outputs=("x", "index", "chksum"),
                       remove_initializers=("for (int i = 0; i < LEN; i++)\n\t\ta[i] = (i * 7) % LEN;",),
                       note="Caller supplies a instead of the pre-timer (i*7)%LEN initializer. Return the original index+x+1, and expose the first maximum, zero-based index and dummy checksum separately."),
    "s318": KernelSpec(read="a", minimum_n=1, scalars=("inc",), scalar_domains=(("inc", "nonnegative_stride"),),
                       strided_vectors=(("a", "inc"),), integer_abs=True, exclude_int_min="a", result="max", result_source="temp",
                       result_expression="max + index+1", dummy_result="chksum", outputs=("max", "index", "chksum"),
                       note="First absolute maximum on ties. index is the logical iteration, not index*inc. Zero stride repeatedly visits a[0]. n*inc must fit int, including the final k increment."),
    "s451": KernelSpec(read="b c", write="a", double_trig=True, test_profile="integer_trig",
                       note="Mixed numeric kernel: choose the original double sin/cos branch; convert integer arguments to double, add in double, then truncate the sum toward zero to int. Requires libm; no float-trig or fast-math substitution."),
    "s481": KernelSpec(read="b c d", update="a", result="stop_index", result_source="termination", termination=True,
                       test_profile="termination", empty_input="No array writes; return -1 (completed without a stop).",
                       note="API adaptation, not process equivalence: replace exit(0) with the first negative d index; return -1 on completion. Test the stop before updating a[i]; preserve the stop element and suffix."),
}

DEFERRED_REASONS = {}
