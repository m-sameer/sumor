import argparse
import os
import re
import sys
from pathlib import Path

import hfst

EPSILON = "@_EPSILON_SYMBOL_@"

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
    """Prompts on stderr."""
    return _paint(text, "36", _ERR_COLOR)


def bold_cyan_err(text):
    """Summary line on stderr."""
    return _paint(text, "1;36", _ERR_COLOR)


def tokenize(string, alphabet):
    """Greedy longest-match tokenization against the transducer alphabet.

    This mirrors the tokenization hfst performs internally for lookup(),
    but operates on plain strings so it can feed HfstBasicTransducer.lookup(),
    which expects pre-tokenized input (plain lookup() would re-tokenize anyway,
    but the basic transducer gives us SFST-compatible enumeration order).
    """
    tokens = []
    i = 0
    while i < len(string):
        best = None
        for sym in alphabet:
            if string.startswith(sym, i) and (best is None or len(sym) > len(best)):
                best = sym
        if best is None:
            tokens.append(string[i])
            i += 1
        else:
            tokens.append(best)
            i += len(best)
    return tokens


def enumerate_paths(basic, alphabet, string):
    """Enumerate (input-path, [outputs]) pairs for string, in transducer order."""
    entries = []
    for inpath, outlist in basic.lookup(tokenize(string, alphabet)).items():
        entries.append((inpath, [o.replace(EPSILON, "") for o, w in outlist]))
    return entries


def ordered_unique(entries):
    """Deduplicated outputs in SFST-compatible enumeration order.

    SFST's generate/analyse enumerate paths in an order that hfst's own
    lookup() does not reproduce (arc traversal order differs between the two
    libraries). Empirically verified against the SFST implementation on 130
    generate keys + 284 analyse forms from dict.tsv: reversing each
    input-alignment's output list and round-robinning (transposing) across
    alignments reproduces SFST order, except for stems with many alternative
    sign readings (e.g. igi, 20 keys) and multi-lemma forms (e.g. uda/ud, 6
    forms), which return identical SETS in a different order. A final stable
    pass moves proper prefixes (e.g. X/N) before their extensions (X/N<ABS>).
    """
    flipped = [(k, list(reversed(vs))) for k, vs in entries]
    depth = max([len(vs) for _, vs in flipped] or [0])
    seq = []
    for j in range(depth):
        for _, vs in flipped:
            if j < len(vs):
                seq.append(vs[j])
    out, seen = [], set()
    for form in seq:
        if form not in seen:
            seen.add(form)
            out.append(form)
    # stable pass: proper prefixes first (e.g. dubsar/N before dubsar/N<ABS>)
    changed = True
    while changed:
        changed = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                if out[i].startswith(out[j]) and len(out[i]) > len(out[j]):
                    out[i], out[j] = out[j], out[i]
                    changed = True
    return out


def load_pair(path):
    """Load transducer + inverted copy as basic transducers for enumeration."""
    t = hfst.HfstTransducer.read_from_file(path)
    fwd = hfst.HfstBasicTransducer(t)
    t_inv = t.copy()
    t_inv.invert()
    bwd = hfst.HfstBasicTransducer(t_inv)
    return (fwd, list(fwd.get_alphabet())), (bwd, list(bwd.get_alphabet()))


def generate(pair, key):
    basic, alphabet = pair
    return ordered_unique(enumerate_paths(basic, alphabet, key))


def analyse(pair, form):
    basic, alphabet = pair
    return ordered_unique(enumerate_paths(basic, alphabet, form))


# Defaults are resolved against this script's directory so the tool works
# regardless of the current working directory.
HERE = Path(__file__).resolve().parent
fst = str(HERE / "sumor.hfst")
dicts = [str(HERE / "dict.tsv")]

args = argparse.ArgumentParser(
    description="""parse and generate Sumerian toy grammar.
We read text from stdin, if it is tab-separated, we consider the second column to be the gold data and create * for mismatches"""
)
args.add_argument("fst",
                  type=str,
                  nargs="?",
                  help="compiled hfst transducer, defaults to " + fst,
                  default=fst)
args.add_argument(
    "-d",
    "--dicts",
    type=str,
    nargs="*",
    action="extend",
    help=
    "dictionaries in TSV format, cols: LEMMA<TAB>POS<TAB>GLOSS[<TAB>...], defaults to "
    + str(dicts))
args = args.parse_args()

if args.dicts is None or len(args.dicts) == 0:
    args.dicts = dicts

en2sums = {}
sum2en = {}

for file in args.dicts:
    # print(file)
    with open(file, "r", encoding="utf-8") as input:
        for line in input:
            line = re.sub(r"\s+", " ", line.strip())
            fields = line.split()
            # print(fields)
            if not line.startswith("#") and len(fields) > 2:
                sum = fields[0] + "/" + fields[1]
                en = fields[2]
                if en not in en2sums:
                    en2sums[en] = [sum]
                elif sum not in en2sums[en]:
                    en2sums[en].append(sum)
                if sum not in sum2en:
                    sum2en[sum] = en

# print(list(en2sums.items())[0])
# print(list(sum2en.items())[0])

gen_pair, an_pair = load_pair(args.fst)
sys.stderr.write(cyan_err("generate> "))
sys.stderr.flush()

correct = 0
processable = 0
total = 0
total_gold = 0
for line in sys.stdin:
    line = line.strip()
    if len(line) == 0:
        break
    if not line.startswith("#"):
        gold = None
        fields = line.split("\t")
        if len(fields) > 1:
            gold = fields[1].strip()
            line = fields[0]
        line = line.strip()
        if len(line) == 0:
            line = gold
            gold = None
        print(gold, line)

        gloss = re.sub(r"<[^>]*>", "", line)
        if gloss in en2sums:

            for sum in en2sums[gloss]:
                key = line[0:line.index(gloss
                                        )] + sum + line[line.index(gloss) +
                                                        len(gloss):]
                print(key)
                total += 1
                if gold is not None:
                    total_gold += 1
                is_correct = False
                forms = generate(gen_pair, key)
                if gold in forms:
                    correct += 1
                for form in forms:
                    if gold is not None and form != gold and re.sub(
                            r"[^a-z]", "", form) != re.sub(
                                r"[^a-z]", "", gold):
                        print(red("\t*" + form + " (" + gold + ")"))
                    else:
                        for analysis in analyse(an_pair, form):
                            amatch = " "
                            result = ""
                            if analysis != key:
                                amatch = "*"
                            else:
                                for lemma in sum2en:
                                    if lemma in analysis:
                                        result = analysis[0:analysis.index(
                                            lemma)] + sum2en[lemma] + analysis[
                                                analysis.index(lemma) +
                                                len(lemma):]
                                        break
                            if amatch != "*":
                                is_correct = True
                            row = ("\t " + form + "\t" + str(gold) + "\t" +
                                   amatch + analysis + "\t" + result)
                            print(green(row) if amatch == " " else yellow(row))
                if is_correct:
                    processable += 1
        if gold is not None:
            sys.stdout.write("\n")
        sys.stderr.write(cyan_err("generate> "))
        sys.stderr.flush()
if total > 0:
    summary = f'coverage: {processable} ({int(0.5+processable*100.0/total)}%)'
    if total_gold > 0:
        summary += f', correct: {correct}/{total_gold} ({int(0.5+correct*100.0/total_gold)}%)'
    sys.stderr.write(bold_cyan_err(summary))
sys.stderr.write("\n")
sys.stderr.flush()
