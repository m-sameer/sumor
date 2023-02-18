import os, sys, re
""" compile signs.tsv into signs.fst """

signs = ["signs.tsv"]

syll2signs = {}

for file in signs:
    with open(file, "rt") as input:
        for line in input:
            if "#" in line:
                line = line[0:line.index("#")]
            line = line.strip()
            if len(line) > 0:
                fields = line.split()
                sign = fields[0].strip()
                sign = "\\-".join(sign.split("-"))
                sign = "\\(".join(sign.split("("))
                sign = "\\)".join(sign.split(")"))
                reading = fields[1].strip()
                if not "(" in sign:
                    if not reading in syll2signs:
                        syll2signs[reading] = [sign]
                    elif not sign in syll2signs[reading]:
                        syll2signs[reading].append(sign)

lhs_rhs = []
for syll, signs in syll2signs.items():
    for sign in signs:
        lhs_rhs.append((syll, sign))
        if len(syll) > 1:
            if re.match(r"^[a-z]", syll[0]):
                lhs_rhs.append((syll[0:1] + "\-" + syll[1:], sign))
            # if re.match(r"^[a-z]",syll[-1]):
            # 	lhs_rhs.append((syll[0:-1]+"\-"+syll[-1:], sign))

lhs_rhs = sorted(set(lhs_rhs))
lhs_rhs = ["{" + lhs + "}:{" + rhs + "}" for lhs, rhs in lhs_rhs]

print("$syll2sign$ = \\\n\t" + " | \\\n\t".join(lhs_rhs))

print("""
% remove final $ and -
$CLEANUP$ = \
    ([a-z0-9A-Z\-]:[a-z0-9A-Z\-])* \
    ([a-z0-9A-Z]:[a-z0-9A-Z]) \
    (\$:<> | \-:<>)?
""")

print('"<length.a>"' + " || $syll2sign$* || $CLEANUP$ ")
