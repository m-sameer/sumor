# SuMor -- Sumerian morphology grammar (HFST)

Toy grammar based on Jagersma, Chap.5. Note that this follows some Jagersma conventions that you won't find in ETCSRI or CDLI. In particular, morphological segmentation is marked by either `=` (nouns) or `-` (verbs).

The grammars are authored in SFST syntax ([flexion.fst](flexion.fst), [experimental/](experimental/)), but compiled to [HFST](https://hfst.github.io/) transducers, which are committed to the repository (`flexion.hfst`, `experimental/*.hfst`). At runtime only the Python [`hfst` package](https://pypi.org/project/hfst/) (see [pyproject.toml](pyproject.toml)) is required -- no SFST installation needed. Regenerating the transducers from the `.fst` sources (`just rebuild-sfst`) optionally uses the `fst-compiler-utf8` toolchain.

## Repository layout

| Path | Contents |
| ---- | -------- |
| `flexion.fst` | Main grammar source (SFST syntax): nominal/verbal inflection |
| `flexion.hfst` | Main grammar, compiled (committed build artifact) |
| `lexicon` | Word list consumed by `flexion.fst` (`cut -f 1 dict.tsv`; regenerable) |
| `dict.tsv` | Bidictionary: `LEMMA<TAB>POS<TAB>GLOSS` (CDLI-based, `N`/`V`/… tags) |
| `test.tsv` | Canned test set: `gloss<FEATURES><TAB>gold-form` pairs |
| `src/sumor/` | Python package: `analyze.py` (CLI + demo), `build.py` (conversion helper) |
| `tests/` | `pytest` suite (`test_sumor.py`) + golden reference outputs (`golden/`) |
| `experimental/` | Prototype pipeline with syllable/sign mapping (see [experimental/Readme.md](experimental/Readme.md)) |
| `experimental/*.hfst` | `sumor` (morphology), `orth` (syllable→sign), `length` (plene writing) transducers |
| `experimental/signs.tsv` | Sign list: `SIGN<TAB>READING` (source of `orth.fst`, via `signs2fst.py`) |
| `data/mtaac-gold/` | CDLI CoNLL files used for evaluation and dictionary building |
| `doc/` | Background material (Jagersma grammar, [slot mapping](doc/slot-mapping.tsv)) |

Intermediate SFST compiler outputs (`*.a`) are git-ignored build artifacts; the committed `*.hfst` files are all that is needed at runtime.

## Requirements & installation

- Python 3.10 (see [.python-version](.python-version))
- The [`hfst`](https://pypi.org/project/hfst/) package (`>=3.16.0.1`, declared in [pyproject.toml](pyproject.toml))

The repository ships a ready-to-use virtualenv at `.venv/` (with `sumor` installed editable via `sumor.pth`). With [`uv`](https://docs.astral.sh/uv/) you can recreate it via `uv sync`; otherwise `pip install hfst` plus `PYTHONPATH=src` suffices to run the tools.

## Quickstart

Build tasks use [`just`](https://just.systems/) (`justfile` at the root and in [experimental/](experimental/); run `just --list` to see all recipes).

```bash
# Verify and run main test set
just && just test

# Run experimental test set
cd experimental && just && just test
```

The `python` path defaults to the project `.venv`; override it per invocation with `just --set python <path-to-python> <recipe>` if your venv lives elsewhere.

---

## Usage

### Main analyzer (`src/sumor`)

Interactive demo of generation (from English gloss + grammatical features) and analysis (of the generated forms):

    $> .venv/bin/python -m sumor

(Or `cut -d ' ' -f 1,3 test.tsv | .venv/bin/python -m sumor` for the canned test set.)

Input lines have the form `gloss<FEATURES>[<TAB>gold-form]`, e.g. `ruler<GEN><ERG>` with gold form `ensi2-ka-ke4`. For each line the analyzer looks up the Sumerian root(s) in [dict.tsv](dict.tsv), generates surface forms with `flexion.hfst`, and re-analyzes them.

For evaluation, optionally provide a "gold" surface form. Only if the predicted surface is a loose match (modulo subscripts and character boundaries), an analysis is performed. Surface forms that do not match are marked with `*`. Analyses that are not identical with the input are marked by `*` (this does not say they are incorrect). A `Total analysis: N, Correct analysis: M` summary is written to stderr.

#### Interpreting the output

On a terminal, output is color-coded:

- 🔴 **red** `*form (gold)` — generated form does not match the gold form
- 🟢 **green** — analysis rows that round-trip exactly to the input key
- 🟡 **yellow** — analysis rows that do not (marked with `*`)
- 🔵 **cyan** — prompts and summary on stderr

Colors are automatically disabled when output is piped (so `just test` stays byte-identical to the reference output) or when the `NO_COLOR` environment variable is set.

#### Library usage

```python
from sumor.analyze import build_dictionaries, norm_cdli
import hfst

# POS normalization (CDLI tags → NOUN/VERB)
assert norm_cdli("N") == "NOUN"
assert norm_cdli("V") == "VERB"

# Load dictionary
en2sums, sum2en = build_dictionaries()  # defaults to dict.tsv
assert en2sums["ruler"] == ["ensik<NOUN>"]

# Transducer lookup
t = hfst.HfstTransducer.read_from_file("flexion.hfst")
tinv = t.copy(); tinv.invert()
for form in ["ensikake", "é"]:
    for analysis, weight in tinv.lookup(form):
        print(form, "=>", analysis.replace("@_EPSILON_SYMBOL_@", ""))
```

Note: The library currently requires transliterations (not transcripts). The workflow expects inputs like `ensi2-ke4`, not `e2`.

<details>
<summary><strong>Generate forms from gloss</strong> (expand)</summary>

```python
from sumor.analyze import build_dictionaries
import hfst

en2sums, sum2en = build_dictionaries()
gloss = "ruler"
key = "ruler<GEN><ERG>"
roots = en2sums[gloss]  # ['ensik<NOUN>']

t = hfst.HfstTransducer.read_from_file("flexion.hfst")
for root in roots:
    # Construct input key: replace gloss with root+POS
    input_key = key.replace(gloss, root)
    # Generate all surface forms
    for form, weight in t.lookup(input_key):
        print(f"{key} → {form.replace('@_EPSILON_SYMBOL_@', '')}")
```
</details>

<details>
<summary><strong>Analyze surface form</strong> (expand)</summary>

```python
import hfst

tinv = hfst.HfstTransducer.read_from_file("flexion.hfst").copy()
tinv.invert()

form = "ensikake"
for analysis, weight in tinv.lookup(form):
    print(f"{form} => {analysis.replace('@_EPSILON_SYMBOL_@', '')}")
# Output: ensikake => ensik<NOUN><GEN><ERG>
```
</details>

<details>
<summary><strong>Round-trip verification</strong> (expand)</summary>

```python
from sumor.analyze import build_dictionaries
import hfst

en2sums, sum2en = build_dictionaries()
t = hfst.HfstTransducer.read_from_file("flexion.hfst")
tinv = t.copy()
tinv.invert()

gloss = "ruler"
key = "ruler<GEN><ERG>"

# Generate
root = en2sums[gloss][0]
input_key = key.replace(gloss, root)
forms = [f[0].replace('@_EPSILON_SYMBOL_@', '') for f in t.lookup(input_key)]

# Analyze and check round-trip
for form in forms:
    for analysis, weight in tinv.lookup(form):
        analysis_clean = analysis.replace('@_EPSILON_SYMBOL_@', '')
        print(f"✓ {key} → {form} → {analysis_clean}")
```
</details>

<details>
<summary><strong>Load multiple dictionaries</strong> (expand)</summary>

```python
from sumor.analyze import build_dictionaries
import hfst

# Load main dict + custom entries
dicts = ["dict.tsv", "custom.tsv"]
en2sums, sum2en = build_dictionaries(dicts)

# Custom.tsv format: LEMMA<TAB>POS<TAB>GLOSS
# with new entries overriding existing ones
```
</details>

### Experimental pipeline (`experimental/`)

The prototype in [experimental/](experimental/) extends the main grammar with syllable segmentation and sign mapping:

- `analyze.py [sumor.hfst]` -- same demo protocol as the main analyzer, but over the experimental dictionary (`lemma/POS` keys) and the `sumor.hfst` transducer, ending in cuneiform-sign transliterations (`dub-sar-ra`). Run via `just test`.
- `translit.py [-fst orth.hfst] <conll>...` -- converts between transliterations and transcriptions for CDLI-CoNLL files using `orth.hfst`; reports coverage at three levels (plain/med/full transcription) and suggests sign-list additions for `signs.tsv`. Run via `just translit`.
- `signs2fst.py`, `conll2dict.py` -- generators for `orth.fst` and `dict.tsv` from `signs.tsv` / CoNLL files.

If you enter a word with features (say, `scribe<DAT>`), it will construct all surface transliterations and then provide all analyses of these. For the target analysis, we consult the bidictionary to predict the gloss.

### Testing

`just test` runs the canned test set and **asserts** the output is byte-identical to the committed golden references in [tests/golden/](tests/golden/) (main: 24 lines, `Total analysis: 15, Correct analysis: 2`; experimental: 54 lines, `coverage: 7 (100%), correct: 7/7 (100%)`); it exits non-zero with a diff on any mismatch. `just translit-test` does the same for the `P100065.conll` transliteration report (19 lines).

`just pytest` runs the [pytest suite](tests/test_sumor.py) (19 tests): unit tests for dictionary building, POS normalization, CLI parsing, no-ANSI-when-piped checks, HFST round-trip, and three golden end-to-end tests. Regenerate references with `just test-update` before committing.

### Development

- `just sync` -- (re)create the project virtualenv (runtime + dev dependencies: `hfst`, `pytest`, `ruff`).
- `just test` / `just pytest` -- asserting pipeline tests / pytest suite.
- `just lint` / `just fmt` -- `ruff check` / `ruff format` over `src/`, `tests/`, `experimental/`.
- `just --set python <path-to-python> <recipe>` -- override venv python per invocation.

### Contributing

Code contributions are welcome under the MIT license (matching CDLI's norm). Data contributions (`dict.tsv`, `signs.tsv`) are CC0-1.0; cite CDLI (https://cdli.earth) for substantial reuse.

Workflow: fork + branch, `just sync && just test && just pytest && just lint`, then PR.

For CDLI-hosted repos, a CLA may be required; see [CDLI Contribute](https://cdli.earth/contribute).

### License

- **Code** (`src/`, `experimental/*.py`, justfiles): [MIT](LICENSE), copyright 2021-2026 Christian Chiarcos and Mohammad Sameer.
- **Data** (`dict.tsv`, `test.tsv`, `lexicon`, `experimental/*.tsv`, `experimental/*.conll`, `data/mtaac-gold/`, `doc/slot-mapping.tsv`): [CC0 1.0 Universal](LICENSE-DATA). This repository hosts no CDLI imagery (non-commercial only, per-holder copyright).

### Known issues

- Support for transliterations as input is imperfect.
- Only the bidictionary defines part of speech; `$GENERATE$` returns both verbal and nominal analyses.
- `$GENERATE$` does not do full nominal slots, but only selected cases.
- `$TRANSLIT$` does not do character segmentation/mapping to characters.
- `$SPELLOUT$` uses impossible allomorphs (`mnrú` > `rú` instead of `munrú` > `mu-rú`).
- `$TRANSLIT$` lets some impossible forms (`*mrú`) slip through.
- Coverage limited to a few IGT glosses and roots.

### History

- 2026-10-11: golden reference tests + pytest suite, asserting `just test` targets, robustness fixes (UTF-8, repo-relative paths, argparse, subprocess), `ruff` linting, MIT (code) + CC0-1.0 (data) licensing, expanded test data (DAT/COM/TERM cases, verbal forms) [MS]
- 2026-10-10: migration from SFST to HFST runtime; committed `.hfst` transducers, ported `analyze.py`/`translit.py`, removed SFST dependencies [MS]
- 2022-11-30: experimental support for transliterations in `experimental/` [CC]
- 2022-04-17 - 2022-10-09 GSoC-2022 project: revision and extension [MS]
- 2021-11-21 created: basic setup, 3 roots [CC]

### Contributors

CC - Christian Chiarcos, GU Frankfurt / U Cologne  
MS - [Mohammad Sameer](https://github.com/m-sameer)