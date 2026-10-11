#!/usr/bin/env python3
"""Build helpers for the SuMor HFST transducers.

The committed *.hfst artifacts are built from the SFST sources (*.fst) with
the fst-compiler-utf8 toolchain and then converted with hfst (see the
justfiles). This module exposes the conversion step; the SFST compile step is
optional and only needed when regenerating the artifacts from changed sources.
"""

import subprocess
import sys
from pathlib import Path

import hfst


def compile_sfst(source="flexion.fst", target="flexion.a", lexicon="lexicon"):
    """Compile an SFST grammar to .a (requires fst-compiler-utf8)."""
    if not Path(lexicon).exists():
        # equivalent of `cut -f 1 dict.tsv > lexicon`
        with open("dict.tsv", encoding="utf-8") as src, open(lexicon, "w", encoding="utf-8") as dst:
            for line in src:
                dst.write(line.split("\t")[0].rstrip("\n") + "\n")
    return subprocess.run(["fst-compiler-utf8", str(source), str(target)]).returncode


def convert_to_hfst(source="flexion.a", target="flexion.hfst"):
    """Convert an SFST .a transducer to HFST .hfst format."""
    t = hfst.HfstTransducer.read_from_file(source)
    print(f"Transducer has {t.number_of_states()} states")
    t.minimize()
    print(f"After minimization: {t.number_of_states()} states")
    t.write_to_file(target)
    print(f"Written: {target}")


def main(argv=None):
    """Convert (and optionally recompile) the grammar transducer."""
    args = argv if argv is not None else sys.argv[1:]
    source = args[0] if len(args) > 0 else "flexion.a"
    target = args[1] if len(args) > 1 else "flexion.hfst"
    if not Path(source).exists():
        fst_source = str(Path(source).with_suffix(".fst"))
        print(f"{source} missing, compiling from {fst_source} ...")
        if compile_sfst(fst_source, source) != 0 or not Path(source).exists():
            print("SFST compile failed (fst-compiler-utf8 not available?).")
            return 1
    convert_to_hfst(source, target)
    print("Done.")


if __name__ == "__main__":
    main()
