% Define the set of valid symbol pairs for the two-level rules.
% The symbol = is used to mark the boundary between the stem and
% the inflectional suffix. It is deleted here.
% \$ is the end symbol
%ALPHABET = [\-A-Za-z0-9é] [\.\=0]:<>

% Read the lexical items from a separate file
$WORDS$ = "lexicon"

% morphophonological rules: generating surface forms
% remove empty morphemes
%$R0$ = {\=0}<=><>

ALPHABET = [\-A-Za-z0-9ø'\(\)] [\.\=0]:<>
$R0$ = (\=:<>) 0<=><>

ALPHABET = [\=A-Za-z0-9ø'\(\)] [\.\-0]:<>
$R1$ = (\-:<>) 0<=><>

$SPELLOUT$ = $R0$ || $R1$

% transliteration
% insertion of character separators and sign numbers seems to be *impossible*
% so we work with a representation that strips off all

 ALPHABET = [\-A-Za-z0-9ø'\(\)]  k:[k<>]
 $k#$ = \
      k <=> k (.:[aeiou])

 ALPHABET = [\-A-Za-z0-9ø'\(\)]  g:[g<>]
 $g#$ = \
      g <=> g (.:[aeiou])

ALPHABET = [\-A-Za-z0-9ø'\(\)]  m:[m<>] n:[n<>]
$n$ =   [mn] <=> <> (.:n)

ALPHABET = [\-A-Za-z0-9ø'\(\)]  m:[m<>] n:[n<>]
$r$ =   [mn] <=> <> (.:r)

ALPHABET = [\-A-Za-z0-9ø'\(\)]  a:[a<>]
$gen$ = \
     a <=> <> (.:ka)

$TRANSLIT$ = $gen$ || $g#$ || $k#$ || $n$ || $r$

% morphological rules: generating deep morphology

% Define a transducer for case endings
% There can be multiple case endings in Sumerian
$NCASE$ = <GEN>:{ak}? <ABL>:{ta}?
$CASE$ = <ABS>:{ø} | <ERG>:{e} | $NCASE$

% rudimentary verbal morphology
% http://oracc.museum.upenn.edu/etcsri/parsing/index.html#VPT
% abbreviations partially changed to match Jagersma
$V1$ = <NEG>:{nu} | <MOD>:{ga} | <MOD>:{ha} | <MOD>:{nan} | <ANT>:{u}
$V2$ = <FIN>:{i}
% $V3$ = <COOR>:{nga}
$V4$ = <VEN>:{mu} | <VEN>:{m}
$V5$ = <MID>:{ba} | <3-SG-NH>:{b}
$V6$ = <2-SG-A>:{e} | <3-SG-H>:{nn} | <3-PL>:{nnee}
$V7$ = <DAT>:a
$V8$ = <COM>:{da}
$V9$ = <ABL>:{ta} | <TERM>:{szi} | <TERM>:{sze}
$V10$ = <L1>:{ni} | <L1-SYN>:{n} | <L2>:{i} | <L3>:{i}
$V11$ = <3-SG-H-A>:{n} | <3-SG-HN-P>:{b} | <3-SG-NH-P>:{b} | <3-SG-NH-L3>:{b}
$V13$ = <PF>:{ed} | <PL>:{ene}
$V14$ = <3-SG-A>:{e} | <3-SG-S>:{ø} | <3-SG-P>:{ø} | <3-PL>:{esz}
% $V15$ = <SUB>:a

% Concatenate the lexical forms and the inflectional endings and
% put a morpheme boundary in between which is not printed in the analysis
$GENERATE$ = \
  $WORDS$ <NOUN>:<> | \
  %  $WORDS$ <NOUN>:<> (<>:\= $NCASE$)* <>:\= $CASE$
  % works, but it's safer to limit recursion depth
  $WORDS$ <NOUN>:<> <>:\= $CASE$ | \
  $WORDS$ <NOUN>:<> <>:\= $NCASE$ <>:\= $CASE$  | \
  $WORDS$ <NOUN>:<> <>:\= $NCASE$ <>:\= $NCASE$ <>:\= $CASE$ |\
  $WORDS$ <NOUN>:<> <>:\= $NCASE$ <>:\= $NCASE$ <>:\= $NCASE$ <>:\= $CASE$ | \
  ($V1$ <>:\-)? \
  ($V2$ <>:\-)? \
  % ($V3$ <>:\-)? \
  ($V4$ <>:\-)? \
  ($V5$ <>:\-)? \
  ($V6$ <>:\- \
    % as soon as one of the following is used, V6 is obligatory
    ($V7$ <>:\-)? \
    ($V8$ <>:\-)? \
    ($V9$ <>:\-)? \
    ($V10$ <>:\-)? )? \
  ($V11$ <>:\-)? \
  $WORDS$ <VERB>:<> \
  (<>:\- $V13$)? \
  (<>:\- $V14$)? \
  % (<>:\- $V15$)?

% Apply the two level rules
% we actually do three levels: transliteration
% The result transducer is stored in the output file
$GENERATE$ || $SPELLOUT$  %|| $TRANSLIT$

% skip $SPELLOUT$ to generate deep morphology from features


