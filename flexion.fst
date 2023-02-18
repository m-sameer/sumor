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


times in msec
 clock   self+sourced   self:  sourced script
 clock   elapsed:              other lines

000.004  000.004: --- NVIM STARTING ---
000.061  000.058: event init
000.190  000.129: early init
000.462  000.272: locale set
000.491  000.030: init first window
000.675  000.184: inits 1
000.690  000.015: window checked
000.692  000.002: parsing arguments
000.964  000.043  000.043: require('vim.shared')
001.026  000.020  000.020: require('vim._meta')
001.027  000.061  000.041: require('vim._editor')
001.028  000.124  000.020: require('vim._init_packages')
001.029  000.213: init lua interpreter
002.165  001.136: expanding arguments
002.220  000.056: inits 2
002.387  000.166: init highlight
002.387  000.001: waiting for UI
002.464  000.076: done waiting for UI
002.467  000.004: clear screen
002.544  000.077: init default mappings
002.551  000.007: init default autocommands
002.987  000.042  000.042: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/ftplugin.vim
003.049  000.017  000.017: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/indent.vim
003.299  000.086  000.086: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/filetype.lua
003.345  000.006  000.006: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/ftplugin.vim
003.388  000.005  000.005: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/indent.vim
003.529  000.043  000.043: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/syntax/synload.vim
003.609  000.178  000.134: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/syntax/syntax.vim
003.703  000.032  000.032: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/filetype.lua
003.748  000.006  000.006: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/ftplugin.vim
004.770  000.975  000.975: sourcing /Users/sameer/.local/share/nvim/site/autoload/plug.vim
005.383  000.015  000.015: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/ftoff.vim
006.235  000.114  000.114: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/filetype.lua
006.299  000.007  000.007: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/ftplugin.vim
006.360  000.006  000.006: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/indent.vim
006.610  000.174  000.174: require('catppuccin')
006.979  000.550  000.376: sourcing /Users/sameer/.local/share/nvim/plugged/catppuccin/colors/catppuccin-macchiato.vim
006.988  003.845  001.865: sourcing /Users/sameer/.config/nvim/init.vim
006.989  000.535: sourcing vimrc file(s)
007.900  000.016  000.016: sourcing /Users/sameer/.local/share/nvim/plugged/wiki.vim/autoload/wiki/init.vim
008.002  000.049  000.049: sourcing /Users/sameer/.local/share/nvim/plugged/wiki.vim/autoload/wiki/u.vim
008.358  000.169  000.169: sourcing /Users/sameer/.local/share/nvim/plugged/wiki.vim/autoload/wiki/tags.vim
008.518  001.030  000.795: sourcing /Users/sameer/.local/share/nvim/plugged/wiki.vim/plugin/wiki.vim
008.827  000.202  000.202: sourcing /Users/sameer/.local/share/nvim/plugged/vim-surround/plugin/surround.vim
008.979  000.050  000.050: sourcing /Users/sameer/.local/share/nvim/plugged/lf.vim/plugin/lf.vim
009.188  000.106  000.106: sourcing /Users/sameer/.local/share/nvim/plugged/vim-floaterm/plugin/floaterm.vim
009.325  000.032  000.032: sourcing /Users/sameer/.local/share/nvim/plugged/lightline.vim/plugin/lightline.vim
009.812  000.162  000.162: sourcing /Users/sameer/.local/share/nvim/plugged/delimitMate/autoload/delimitMate.vim
010.659  001.217  001.054: sourcing /Users/sameer/.local/share/nvim/plugged/delimitMate/plugin/delimitMate.vim
011.278  000.084  000.084: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/gzip.vim
011.317  000.007  000.007: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/health.vim
011.945  000.098  000.098: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/pack/dist/opt/matchit/plugin/matchit.vim
012.992  001.645  001.546: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/matchit.vim
013.131  000.098  000.098: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/matchparen.vim
013.342  000.176  000.176: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/netrwPlugin.vim
013.465  000.081  000.081: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/rplugin.vim
013.561  000.038  000.038: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/shada.vim
013.623  000.015  000.015: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/spellfile.vim
013.717  000.056  000.056: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/tarPlugin.vim
013.825  000.069  000.069: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/tohtml.vim
013.883  000.016  000.016: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/tutor.vim
014.012  000.090  000.090: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/zipPlugin.vim
015.139  000.051  000.051: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/editorconfig.lua
015.251  000.068  000.068: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/man.lua
015.334  000.036  000.036: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/plugin/nvim.lua
015.354  003.199: loading rtp plugins
015.553  000.199: loading packages
015.938  000.385: loading after plugins
015.946  000.008: inits 3
016.903  000.957: reading ShaDa
017.005  000.102: opening buffers
017.279  000.209  000.209: sourcing /Users/sameer/.local/share/nvim/plugged/lightline.vim/autoload/lightline.vim
017.573  000.034  000.034: sourcing /Users/sameer/.local/share/nvim/plugged/lightline.vim/autoload/lightline/tab.vim
017.835  000.098  000.098: sourcing /Users/sameer/.local/share/nvim/plugged/lightline.vim/autoload/lightline/colorscheme.vim
018.177  000.517  000.419: sourcing /Users/sameer/.local/share/nvim/plugged/lightline.vim/autoload/lightline/colorscheme/one.vim
020.690  002.924: BufEnter autocommands
020.692  000.002: editing files in windows
020.755  000.064: VimEnter autocommands
020.756  000.001: UIEnter autocommands
020.940  000.104  000.104: sourcing /opt/homebrew/Cellar/neovim/HEAD-d89290b/share/nvim/runtime/autoload/provider/clipboard.vim
020.943  000.083: before starting main loop
021.091  000.148: first screen update
021.092  000.001: --- NVIM STARTED ---


times in msec
 clock   self+sourced   self:  sourced script
 clock   elapsed:              other lines

000.011  000.011: --- NVIM STARTING ---
000.058  000.047: event init
000.151  000.093: early init
000.269  000.117: locale set
000.297  000.028: init first window
006.242  005.945: inits 1
006.253  000.011: window checked
006.255  000.002: parsing arguments
006.530  000.044  000.044: require('vim.shared')
006.589  000.020  000.020: require('vim._meta')
006.590  000.059  000.039: require('vim._editor')
006.591  000.125  000.022: require('vim._init_packages')
006.592  000.213: init lua interpreter
006.853  000.260: expanding arguments
006.865  000.013: inits 2
007.037  000.172: init highlight
