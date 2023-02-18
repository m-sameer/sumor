all:
		cut -f 1 dict.tsv > lexicon
		fst-compiler-utf8 flexion.fst flexion.a

test_cdli:
	# update to YOUR CDLI files:
	cut -f 1 dict.tsv > lexicon
	fst-compiler flexion.fst flexion.a
# 	fst-generate flexion.a
# 	cat lexicon | perl -pe 's/\s+/ /g;'
# 	echo;
# 	fst-mor flexion.a
	
	#  test on CDLI files
	cut -d " " -f 1,3 test.tsv | python3 analyze.py flexion.a -d dict.tsv
	## use -f 1,2 to evaluate morphological forms, but then lexicon, etc., must be adapted

test: all
#		fst-generate flexion.a
#		cat lexicon | perl -pe 's/\s+/ /g;'
#		echo;
#		fst-mor flexion.a
	cut -d ' ' -f 1,3 test.tsv | python3 analyze.py

