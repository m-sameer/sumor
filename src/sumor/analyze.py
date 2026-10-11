#!/usr/bin/env python3
"""Analyze/generate Sumerian forms using the HFS grammar.

This module provides a drop-in replacement for the original sfst-based analyze.py.
"""

import argparse
import os
import sys
import re
from pathlib import Path

import hfst

EPSILON = "@_EPSILON_SYMBOL_@"

# Repository root (this file lives at <root>/src/sumor/analyze.py). Default
# transducer and dictionary paths are resolved against it so the CLI works
# regardless of the current working directory.
ROOT = Path(__file__).resolve().parents[2]

# ANSI colors for terminal output. Automatically disabled when piped
# (so `just test` output stays byte-identical to the reference output)
# or when the NO_COLOR environment variable is set.
_STD_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
_ERR_COLOR = sys.stderr.isatty() and os.environ.get("NO_COLOR") is None


def _paint(text, code, enabled):
    """Wrap text in an ANSI color code unless colors are disabled."""
    return f"\033[{code}m{text}\033[0m" if enabled else text


def red(text):
    """Mismatch lines: generated form does not match the gold form."""
    return _paint(text, "31", _STD_COLOR)


def green(text):
    """Analysis rows that round-trip exactly to the input key."""
    return _paint(text, "32", _STD_COLOR)


def yellow(text):
    """Analysis rows that do not round-trip (marked with *)."""
    return _paint(text, "33", _STD_COLOR)


def cyan_err(text):
    """Prompts and summary on stderr."""
    return _paint(text, "36", _ERR_COLOR)

def norm_cdli(pos):
    """Return NOUN or VERB for CDLI tag."""
    if pos.endswith("N"):
        return "NOUN"
    if pos.startswith("V") or pos.startswith("NU") or pos.startswith("NF.V"):
        return "VERB"
    return pos

def build_dictionaries(paths=None):
    """Build en2sums and sum2en from dict.tsv-style files.

    Gloss-to-key and key-to-gloss mappings; later files take precedence
    only for new entries (existing entries are kept).
    """
    if not paths:
        paths = [ROOT / 'dict.tsv']
    en2sums = {}
    sum2en = {}
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                line = re.sub(r'\s+', ' ', line.strip())
                fields = line.split()
                if len(fields) > 2:
                    lemma = fields[0]
                    pos = norm_cdli(fields[1])
                    gloss = fields[2]
                    sum_form = lemma + '<' + pos + '>'
                    if gloss not in en2sums:
                        en2sums[gloss] = []
                    if sum_form not in en2sums[gloss]:
                        en2sums[gloss].append(sum_form)
                    if sum_form not in sum2en:
                        sum2en[sum_form] = gloss
    return en2sums, sum2en

def parse_args(argv=None):
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate and analyze Sumerian forms. "
                    "Input lines have the form 'gloss<FEATURES>[ gold-form]'.")
    parser.add_argument(
        "fst",
        nargs="?",
        default=str(ROOT / "flexion.hfst"),
        help="compiled HFST transducer, defaults to the repository flexion.hfst")
    parser.add_argument(
        "-d", "--dicts",
        nargs="*",
        action="extend",
        default=None,
        help="dictionaries in TSV format, cols: LEMMA<TAB>POS<TAB>GLOSS; "
             "defaults to the repository dict.tsv")
    return parser.parse_args(argv)

def main(argv=None):
    """CLI: analyze based on stdin."""
    args = parse_args(argv)

    t = hfst.HfstTransducer.read_from_file(args.fst)
    t_inv = t.copy()
    t_inv.invert()

    en2sums, sum2en = build_dictionaries(args.dicts)

    sys.stderr.write(cyan_err("generate> "))
    sys.stderr.flush()

    correct = 0
    total = 0
    
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0]
            gold = parts[1]
            total += 1
        else:
            key = line
            gold = None
        
        gloss = re.sub(r'<[^>]*>', '', key)
        if gloss in en2sums:
            for sum_form in en2sums[gloss]:
                key_idx = key.index(gloss)
                full_key = key[:key_idx] + sum_form + key[key_idx + len(gloss):]

                forms = [o for o, w in t.lookup(full_key)]

                for form in forms:
                    form = form.replace(EPSILON, '')
                    if gold is not None and form != gold:
                        norm_form = re.sub(r'[^a-z]', '', form.lower())
                        norm_gold = re.sub(r'[^a-z]', '', gold.lower())
                        if norm_form != norm_gold:
                            sys.stdout.write(red("\t*" + form + " (" + gold + ")\n"))
                            continue
                    for analysis, _weight in t_inv.lookup(form):
                        analysis = analysis.replace(EPSILON, '')
                        amatch = " "
                        result = ""
                        if analysis != full_key:
                            amatch = "*"
                        else:
                            for lemma_pos in sum2en:
                                if lemma_pos in analysis:
                                    result = analysis[:analysis.index(lemma_pos)] + sum2en[lemma_pos] + analysis[analysis.index(lemma_pos) + len(lemma_pos):]
                                    break
                        if amatch != "*":
                            correct += 1
                        row = "\t " + form + "\t" + str(gold) + "\t" + amatch + analysis + "\t" + result + "\n"
                        sys.stdout.write(green(row) if amatch == " " else yellow(row))

        if gold is not None:
            sys.stdout.write("\n")
        
        sys.stderr.write(cyan_err("generate> "))
        sys.stderr.flush()

    sys.stderr.write(_paint(f"Total analysis: {total}, Correct analysis: {correct}\n", "1;36", _ERR_COLOR))
    sys.stderr.write("bye!\n")

if __name__ == '__main__':
    main()