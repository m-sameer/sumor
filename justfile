# SuMor build tasks (HFST-based; no SFST toolchain needed except rebuild-sfst).
# Recipes work from any directory; all paths are anchored at this justfile.

python := justfile_directory() + "/.venv/bin/python"
root := justfile_directory()

# Default: verify the committed transducer is present.
check-hfst:
    @test -f {{root}}/flexion.hfst || (echo "flexion.hfst missing; run 'just rebuild-sfst' (requires fst-compiler-utf8) to regenerate" && exit 1)

# Optional: rebuild from SFST source (requires fst-compiler-utf8 + libsfst).
rebuild-sfst:
    cd {{root}} && (test -f lexicon || cut -f 1 dict.tsv > lexicon) && fst-compiler-utf8 flexion.fst flexion.a && {{python}} -c "import hfst; t = hfst.HfstTransducer.read_from_file('flexion.a'); t.minimize(); t.write_to_file('flexion.hfst')"

# Regenerate the word list consumed by flexion.fst (skipped if present).
lexicon:
    cd {{root}} && test -f lexicon || cut -f 1 dict.tsv > lexicon

# Sync the project virtualenv (runtime + dev dependencies).
sync:
    cd {{root}} && uv sync

# Run the canned test set and assert byte-parity with the golden reference (-u keeps the merged stream order deterministic).
test: check-hfst
    @rm -f /tmp/sumor-main-test.txt && cd {{root}} && cut -d ' ' -f 1,3 test.tsv | {{python}} -u -m sumor > /tmp/sumor-main-test.txt 2>&1 && diff -u {{root}}/tests/golden/main.txt /tmp/sumor-main-test.txt && rm -f /tmp/sumor-main-test.txt && echo "main: byte-identical to tests/golden/main.txt"

# Regenerate the golden reference (only when the output change is intended).
test-update: check-hfst
    cd {{root}} && cut -d ' ' -f 1,3 test.tsv | {{python}} -u -m sumor > tests/golden/main.txt 2>&1 && wc -l tests/golden/main.txt

# Run the pytest suite (unit + golden tests).
pytest:
    cd {{root}} && {{python}} -m pytest tests/ -q

# Lint the Python sources.
lint:
    cd {{root}} && {{python}} -m ruff check src tests experimental

# Format the Python sources.
fmt:
    cd {{root}} && {{python}} -m ruff format src tests experimental

# Remove regenerable intermediates (committed .hfst and tracked lexicon are kept).
clean:
    rm -f {{root}}/flexion.a
