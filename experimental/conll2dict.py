import argparse, sys, os, re

args = argparse.ArgumentParser(description="get dict from CDLI-CoNLL")
args.add_argument("files",
                  type=str,
                  nargs="+",
                  help="CoNLL files to read from")
form_col = 1
args.add_argument("-f",
                  "--form_col",
                  type=int,
                  help=f"FORM column, defaults to {form_col}",
                  default=form_col)
seg_col = 2
args.add_argument("-s",
                  "--seg_col",
                  type=int,
                  help=f"SEGM column, defaults to {seg_col}",
                  default=seg_col)
pos_col = 3
args.add_argument("-p",
                  "--pos_col",
                  type=int,
                  help=f"POS column, defaults to {pos_col}",
                  default=pos_col)

args = args.parse_args()

en2sum2freq = {}
sum2en2freq = {}

# we normalize to NV, N, V and X (indeclinable)
xpos2pos = {
    "NU": "NV",
    "NF.V": "NV",
    "MN": "N",
    "PN": "N",
    "RN": "N",
    "N": "N",
    "V": "V",
    "CNJ": "X"
}

for file in args.files:
    with open(file, "rt", errors="ignore") as input:
        for line in input:
            if "#" in line:
                line = line[0:line.index("#")]  # strip comments
            line = line.strip()
            fields = line.split("\t")
            if len(fields) > max(args.form_col, args.seg_col, args.pos_col):

                pos = fields[args.pos_col].split(".")
                for xpos in xpos2pos:
                    if xpos in pos:
                        pos = [xpos2pos[xpos]]
                        break
                pos = pos[0]
                if not pos in xpos2pos.values():
                    sys.stderr.write("warning: unknown POS tag in " +
                                     fields[args.pos_col] + "\n")
                    pos = "X"

                lemma_gloss = fields[args.seg_col]
                for chunk in lemma_gloss.split("-"):
                    if re.match(r".*[a-z0-1A-Z].*\[.*", chunk):
                        lemma_gloss = chunk
                        break
                if not "[" in lemma_gloss:
                    break
                lemma = lemma_gloss.split("[")[0]
                gloss = lemma_gloss.split("[")[1].split("]")[0]
                try:
                    x = int(gloss)
                    gloss = lemma
                    lemma = lemma.lower()
                except Exception:
                    pass
                lemma = lemma.strip()
                gloss = gloss.strip()
                if len(lemma) > 0 and len(gloss) > 0:
                    print(lemma + "\t" + pos + "\t" + gloss)
