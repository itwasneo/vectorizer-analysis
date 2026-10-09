#!/usr/bin/env python3
"""Extract the 151 TSVC cases into self-contained, integer-typed C executables.

This is a TSVC-based *adaptation*, not the 149-case dataset from LLM-Vectorizer.
The computational kernels are copied verbatim; the shared setup uses integers.
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "llvm-test-suite/MultiSource/Benchmarks/TSVC/tsc.inc"
FUNCTION = re.compile(r"^(?:int|void|TYPE)\s+([a-zA-Z_]\w*)\s*\([^;{}]*\)\s*\{", re.M)
CALL = re.compile(r"^\s*((?:s\d+|v[a-z]+))\([^;]*\);\s*$", re.M)


def closing_brace(source: str, opening: int) -> int:
    """Find the closing brace, ignoring braces in strings and C comments."""
    depth = 0
    state = "code"
    i = opening
    while i < len(source):
        c = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""
        if state == "code":
            if c == "/" and nxt == "/":
                state, i = "line", i + 2
                continue
            if c == "/" and nxt == "*":
                state, i = "block", i + 2
                continue
            if c in "\"'":
                state, quote = "quote", c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
        elif state == "line" and c == "\n":
            state = "code"
        elif state == "block" and c == "*" and nxt == "/":
            state, i = "code", i + 2
            continue
        elif state == "quote":
            if c == "\\":
                i += 2
                continue
            if c == quote:
                state = "code"
        i += 1
    raise ValueError("unbalanced function body")


def functions(source: str) -> dict[str, tuple[int, int, str]]:
    result = {}
    for match in FUNCTION.finditer(source):
        end = closing_brace(source, match.end() - 1)
        name = match.group(1)
        if name in result:
            raise ValueError(f"duplicate function: {name}")
        result[name] = (match.start(), end, source[match.start():end])
    return result


def generate(source_path: Path, output: Path) -> None:
    source = source_path.read_text()
    funcs = functions(source)
    if "main" not in funcs or "s000" not in funcs:
        raise ValueError("unexpected TSVC source layout")
    main = funcs["main"][2]
    calls = {}
    for match in CALL.finditer(main):
        name = match.group(1)
        if name in calls:
            raise ValueError(f"duplicate benchmark call: {name}")
        calls[name] = match.group(0).strip()
    if len(calls) != 151 or not all(name in funcs for name in calls):
        raise ValueError(f"expected 151 defined cases, got {len(calls)}")

    # Everything preceding the first benchmark is shared setup: globals,
    # initializers, check(), etc. Remove the first category's opening #if.
    prefix = source[:funcs["s000"][0]]
    prefix = re.sub(r"#if TESTS & LINEAR_DEPENDENCE\s*\Z", "", prefix)
    prefix = prefix.replace('#include "types.h"',
                            '#define LEN 32000\n#define LEN2 256\n#define TYPE int\n#define X_TYPE int\n#define ALIGNMENT 32\n#define FABS(x) abs(x)')
    prefix = prefix.replace('#include "tests.h"', '')
    # The original fractional initializers mostly become zeros with TYPE=int.
    # Choose small positive integers instead, to make integer data useful.
    prefix = prefix.replace('1. / (TYPE) (i+1)', '1 + (i % 7)')
    prefix = prefix.replace('1. / (TYPE) ((i+1) * (i+1))', '1 + (i % 11)')
    # The original check() passes int values to printf("%G"), which is UB.
    check_match = re.search(r"^void check\(int name\)\s*\{", prefix, re.M)
    if not check_match:
        raise ValueError("check() not found")
    check_end = closing_brace(prefix, check_match.end() - 1)
    prefix = (prefix[:check_match.start()] + '''void check(int name) {
    unsigned long long hash = (unsigned)name;
    for (int i = 0; i < LEN; ++i) {
        hash = hash * 33u + (unsigned)a[i];
        hash = hash * 33u + (unsigned)b[i];
        hash = hash * 33u + (unsigned)c[i];
        hash = hash * 33u + (unsigned)d[i];
        hash = hash * 33u + (unsigned)e[i];
        hash = hash * 33u + (unsigned)x[i];
        hash = hash * 33u + (unsigned)indx[i];
    }
    for (int i = 0; i < LEN2; ++i)
        for (int j = 0; j < LEN2; ++j) {
            hash = hash * 33u + (unsigned)aa[i][j];
            hash = hash * 33u + (unsigned)bb[i][j];
            hash = hash * 33u + (unsigned)cc[i][j];
            hash = hash * 33u + (unsigned)tt[i][j];
        }
    printf("%llu\\n", hash * 33u + (unsigned)temp);
}
''' + prefix[check_end:])
    # Some kernels call these other (non-benchmark) functions.
    helpers = {name: funcs[name][2] for name in ("s151s", "s152s", "test", "max", "min", "set")}
    dummy = '''int dummy(TYPE a[LEN], TYPE b[LEN], TYPE c[LEN], TYPE d[LEN],
    TYPE e[LEN], TYPE aa[LEN2][LEN2], TYPE bb[LEN2][LEN2],
    TYPE cc[LEN2][LEN2], TYPE s) {
    (void)a; (void)b; (void)c; (void)d; (void)e;
    (void)aa; (void)bb; (void)cc; (void)s;
    return 0;
}
'''
    output.mkdir(parents=True, exist_ok=True)
    for name, call in calls.items():
        # Include helper definitions for kernels that call them; omit all
        # other benchmark functions.
        dependencies = {
            "s151": ("s151s",), "s152": ("s152s",),
            "s31111": ("test",),
        }
        selected_helpers = [helpers[h] for h in dependencies.get(name, ())]
        # Include min/max even where unused: some cases call these helpers.
        selected_helpers += [helpers[h] for h in ("min", "max") if h not in dependencies.get(name, ())]
        program = '\n\n'.join((
            f'/* Extracted from {source_path.name}: {name}. Integer adaptation; see README. */',
            prefix, *selected_helpers, funcs[name][2], helpers["set"], dummy,
            f'''int main(int argc, char **argv) {{
    int n1 = 1, n3 = 1;
    TYPE s1, s2;
    int *ip = NULL;
    ntimes = argc > 1 ? atoi(argv[1]) : 1;
    if (ntimes < 1 || ntimes > 100) {{
        fprintf(stderr, "ntimes must be between 1 and 100\\n");
        return 2;
    }}
    if (posix_memalign((void **)&ip, ALIGNMENT, LEN * sizeof(*ip))) return 2;
    set(ip, &s1, &s2);
    {call}
    free(ip);
    free(xx);
    return 0;
}}''',
        )) + '\n'
        (output / f'{name}.c').write_text(program)
    (output / 'manifest.json').write_text(json.dumps(list(calls), indent=2) + '\n')
    (output / 'README.md').write_text('''# TSVC integer adaptations

One self-contained C translation unit per case; `manifest.json` lists all 151.
Generated from the repository's `tsc.inc` using `scripts/extract_tsvc_int.py`.
The kernel bodies are copied unchanged. The shared setup is converted to
`int` arrays; fractional initializers are replaced by small positive integers,
and the original floating-point checksum is replaced by an integer hash.
Each case still contains the original outer `ntimes` loop, `init()` calls,
global state, and fixed array sizes; these are NOT the paper's standalone
parameterized 149 functions. Integer arithmetic can overflow; division or
out-of-bounds accesses are possible in individual kernels. Compilation is
not evidence of safe execution or semantic equivalence. Audit each case and
its input invariants before using it for differential testing or Alive2.

Compile a case on your target host with e.g.:

    clang -std=c11 -O0 -fsyntax-only s124.c
    clang -std=c11 -O2 s124.c -lm -o s124
    ./s124 1

Do not compare these checksums to the upstream floating-point reference output.
''')
    print(f'Generated {len(calls)} C files in {output}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path, default=ROOT / 'generated/tsvc-int')
    args = parser.parse_args()
    generate(args.source, args.output)


if __name__ == '__main__':
    main()
