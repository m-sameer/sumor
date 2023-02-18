import sfst
import sys, os, re, traceback, argparse
""" 

	conversion between transliterations and transcriptions for Sumerian/cuneiform,
	based on the MTAAC gold corpus (https://github.com/cdli-gh/mtaac_gold_corpus),
	cf. https://cdli.ox.ac.uk/wiki/doku.php?id=sumerian:transliteration_and_the_diacritics

	- transliteration: sign-by-sign representation of the cuneiform signs in question: each cuneiform sign is given a reading and when these readings form part of a single word, they are linked by hyphens. 

		dub-sar-ra

	- transcription: redundant elements are removed and the morphological structure of the phrase is indicated in one way or another.

		dubsar=a (scribe.DAT)
		
	Often, transliterations are ambiguous, so the very same transliteration could also be read as

		dubsar=ak (scribe.GEN)

	Note that we don't count transliteration errors of numbers because these are not processable by the SFST system (they use round brackets)

"""

#######
# aux #
#######


def get_med_transc(transc):
    """ cut off implicit prefixes and suffixes, keep implicit infixes """

    DEBUG = False

    if DEBUG: print("\nmed_transc", transc, end="\t")

    transc = "]<".join(transc.split("]"))
    transc = ">[".join(transc.split("["))
    transc = re.sub(r"^([^<]*>)", r"<\1", transc)
    transc = re.sub(r"(<[^>]*)$", r"\1>", transc)
    if DEBUG: print(transc, end="\t")

    transc = "".join(transc.split("<>"))
    if DEBUG: print(transc, end="\t")

    transc = re.sub(r"^[^<]*<", "", transc)
    transc = re.sub(r">[^>]*$", "", transc)
    transc = re.sub(r"[<>\[\]]", "", transc)
    if DEBUG: print(transc)

    return transc


##########
# config #
##########

args = argparse.ArgumentParser(description="""
	Read transliterations and produce transcriptions and vice versa using SFST transducers.
	This is to be applied to CDLI CoNLL files and will produce a list of unanalyzed forms.
	""")
args.add_argument("files",
                  type=str,
                  nargs="+",
                  help="CoNLL files to read from")

fst = "orth.a"
args.add_argument("-fst",
                  "--fst",
                  type=str,
                  help="compiled SFST transducer, defaults to " + fst,
                  default=fst)

form_col = 1
args.add_argument("-f",
                  "--form_col",
                  type=int,
                  help=f"FORM column, defaults to {form_col}",
                  default=form_col)

segm_col = 2
args.add_argument("-s",
                  "--segm_col",
                  type=int,
                  help=f"SEGM column, defaults to {segm_col}",
                  default=segm_col)

pos_col = 3
args.add_argument("-p",
                  "--pos_col",
                  type=int,
                  help=f"POS column, defaults to {pos_col}",
                  default=pos_col)

args = args.parse_args()

########
# init #
########

sfst.init(args.fst)

#################
# process CoNLL #
#################

# we produce three kinds of transliterations
# - plain transcription: strip all "implicit" phonemes
# - med transcription:   strip implicit prefixes and suffixes, keep internal implicits
# - full transcription:  keep all implicits
# as the Ur III orthography allows to just not write morphology,
# a sufficient criterion for success is to capture plain and med transcriptions
# full transcriptions are a bonus (but probably just infeasible), so we
# don't report it as an error of these are not produced

total = 0
med_ok = 0
full_ok = 0
plain_ok = 0

additions = []

for file in args.files:
    with open(file, "rt", errors="ignore") as input:
        for line in input:
            if "#" in line:
                line = line[0:line.index("#")]  # strip comments
            line = line.strip()
            fields = line.split("\t")
            if len(fields) > max(args.form_col, args.segm_col):

                transl = fields[args.form_col]
                gloss = fields[args.segm_col]
                pos = "_"

                if len(fields) > args.pos_col:
                    pos = fields[args.pos_col]

                if not "(" in transl:
                    total += 1

                    transc = re.sub(r"([^\-])\[[^\-\]]*\]", r"\1", gloss)
                    transc = re.sub(r"[ø]", "", transc)
                    transc = "".join(transc.split("-")).lower()

                    plain_transc = re.sub(r"\[[^\]]*\]", "", transc)
                    full_transc = re.sub(r"[\[\]]", "", transc)

                    transl_nodet = re.sub(r"{[^}]*}", "", transl)

                    med_transc = get_med_transc(transc)

                    # print("\n",gloss,transc,full_transc,med_transc,plain_transc)

                    for transc in set([plain_transc, med_transc, full_transc]):
                        cands = sfst.generate(transc)
                        if transl_nodet in cands:
                            if transc == full_transc: full_ok += 1
                            if transc == med_transc: med_ok += 1
                            if transc == plain_transc: plain_ok += 1
                        elif transc in [plain_transc, med_transc]:
                            if "-" in transl_nodet:
                                if not "(" in transl_nodet:
                                    # these cannot be processed by SFST and will always fail
                                    print(
                                        f"\ngap detected for transcription {transc}:"
                                    )
                                    print("transliteration:", transl)
                                    print("gold annotation:",
                                          gloss + " (= " + pos + ")")
                                    print(
                                        f"{len(cands)} predicted transliterations:\n"
                                        + " " * 17 +
                                        ("\n" + " " * 17).join(cands))
                            elif transc == plain_transc:
                                additions.append((transl_nodet + "-", transc))
                            elif transc == med_transc:
                                additions.append((transl_nodet + "$", transc))

                    if total > 0:
                        sys.stderr.write(
                            f"\radding {file}, analyzed: {total}, accuracy: {int(plain_ok*100.0/total)}% (no implicits), {int(med_ok*100.0/total)}% (no implicit prefixes and suffixes), {int(full_ok*100.0/total)}% (incl. implicits)"
                        )

    if total > 0:
        sys.stderr.write(
            f"\radding {file}, analyzed: {total}, accuracy: {int(plain_ok*100.0/total)}% (no implicits), {int(med_ok*100.0/total)}% (no implicit prefixes and suffixes), {int(full_ok*100.0/total)}% (incl. implicits)\n"
        )

sign2transes = {}
for sign, transl in additions:
    if not sign in sign2transes: sign2transes[sign] = []
    if not transl in sign2transes[sign]: sign2transes[sign].append(transl)

if len(sign2transes) > 0:
    print("\nsignary additions:")
    for sign, ts in sorted(sign2transes.items()):
        for t in sorted(ts):
            print(sign, "\t", t)
