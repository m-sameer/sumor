# SuMor experimental pipeline (HFST)

Toy grammar extension with syllable segmentation and sign mapping.

Build with

    just

(`just` verifies the committed `.hfst` transducers; `just rebuild-sfst` recompiles them from the `.fst` sources with `fst-compiler-utf8`.)

Test with

    just test

Transliteration evaluation against CDLI-CoNLL files:

    just translit    # Evaluate P100065.conll
    just translit-test  # Assert byte-identical against golden

## License

Inherits the root [LICENSE](../LICENSE) (code) and [LICENSE-DATA](../LICENSE-DATA) (data).

## Building the sign list

Key to this enterprise is to extend `signs.tsv`.

In order to do that, process one or more CDLI-CoNLL files and return transcriptions that cannot be reproduced. Then, extend `signs.tsv` manually.

To evaluate against `P100065.conll`:

    just        # Verify .hfst files
    just translit

Check the output for "gap detected" entries and extend `signs.tsv` accordingly.

## API

The experimental `analyze.py` is a demo (not a stable API). For programmatic use, import the main `sumor.analyze` module instead.