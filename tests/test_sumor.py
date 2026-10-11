"""Tests for the SuMor HFST toolchain.

Golden tests compare pipeline output byte-for-byte against the reference
outputs in tests/golden/. Colors are disabled automatically because the
test harness always pipes the tools' stdout/stderr.
"""

import os
import subprocess
import sys
from pathlib import Path

import hfst
import pytest

from sumor import analyze
from sumor import build as build_mod

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"
EXP = ROOT / "experimental"


def run_tool(args, cwd, stdin_bytes=None):
    """Run a tool with piped stdio, return (returncode, merged output).

    stderr is merged into stdout (like shell `2>&1`) so the comparison
    sees the true write order. `-u` forces unbuffered binary I/O so that
    order is deterministic regardless of environment buffering settings.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-u", *args],
        input=stdin_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=env,
    )
    return proc.returncode, proc.stdout


def cut_test_input():
    """First and third space-separated columns of the main test.tsv."""
    cols = []
    for line in (ROOT / "test.tsv").read_text(encoding="utf-8").splitlines():
        parts = line.split(" ")
        if len(parts) >= 3:
            cols.append(f"{parts[0]} {parts[2]}")
        else:
            cols.append(line)
    return ("\n".join(cols) + "\n").encode("utf-8")


@pytest.mark.parametrize(
    "pos, expected",
    [
        ("N", "NOUN"),
        ("MN", "NOUN"),
        ("NU", "VERB"),
        ("V", "VERB"),
        ("NF.V", "VERB"),
        # unknown tags (incl. experimental "NV") pass through unchanged
        ("NV", "NV"),
        ("X", "X"),
    ],
)
def test_norm_cdli(pos, expected):
    assert analyze.norm_cdli(pos) == expected


def test_epsilon_constant():
    assert analyze.EPSILON == "@_EPSILON_SYMBOL_@"


def test_build_dictionaries(tmp_path):
    (tmp_path / "d.tsv").write_text(
        "# comment\n"
        "ga\tN\thouse\n"
        "ga\tN\thouse\n"  # duplicate: kept once
        "ensi2.k\tN\truler\n",
        encoding="utf-8",
    )
    en2sums, sum2en = analyze.build_dictionaries([tmp_path / "d.tsv"])
    assert en2sums == {"house": ["ga<NOUN>"], "ruler": ["ensi2.k<NOUN>"]}
    assert sum2en == {"ga<NOUN>": "house", "ensi2.k<NOUN>": "ruler"}


def test_build_dictionaries_default():
    en2sums, sum2en = analyze.build_dictionaries()
    assert en2sums["ruler"] == ["ensik<NOUN>"]
    assert sum2en["ensik<NOUN>"] == "ruler"


def test_parse_args_defaults():
    args = analyze.parse_args([])
    assert args.fst == str(ROOT / "flexion.hfst")
    assert args.dicts is None


def test_parse_args_explicit(tmp_path):
    args = analyze.parse_args(["custom.hfst", "-d", "a.tsv", "b.tsv"])
    assert args.fst == "custom.hfst"
    assert args.dicts == ["a.tsv", "b.tsv"]


def test_lookup_has_no_epsilon_markers():
    t = hfst.HfstTransducer.read_from_file(str(ROOT / "flexion.hfst"))
    t_inv = t.copy()
    t_inv.invert()
    for form in ["ensikake", "gaø"]:
        for analysis, _weight in t_inv.lookup(form):
            cleaned = analysis.replace(analyze.EPSILON, "")
            assert analyze.EPSILON not in cleaned


def test_no_ansi_when_piped():
    rc, out = run_tool(["-m", "sumor"], cwd=ROOT, stdin_bytes=cut_test_input())
    assert rc == 0
    assert b"\x1b[" not in out


def test_no_ansi_with_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    rc, out = run_tool(["-m", "sumor"], cwd=ROOT, stdin_bytes=cut_test_input())
    assert rc == 0
    assert b"\x1b[" not in out


def test_golden_main():
    rc, out = run_tool(["-m", "sumor"], cwd=ROOT, stdin_bytes=cut_test_input())
    assert rc == 0
    assert out == (GOLDEN / "main.txt").read_bytes()


def test_golden_experimental():
    stdin_bytes = (EXP / "test.tsv").read_bytes()
    rc, out = run_tool(["analyze.py"], cwd=EXP, stdin_bytes=stdin_bytes)
    assert rc == 0
    assert out == (GOLDEN / "experimental.txt").read_bytes()


def test_golden_translit():
    rc, out = run_tool(["translit.py", "P100065.conll"], cwd=EXP)
    assert rc == 0
    assert out == (GOLDEN / "translit.txt").read_bytes()


def test_convert_to_hfst_roundtrip(tmp_path):
    src = tmp_path / "tiny.a"
    dst = tmp_path / "tiny.hfst"
    hfst.regex("a:b").write_to_file(str(src))
    build_mod.convert_to_hfst(str(src), str(dst))
    assert dst.exists()
    back = hfst.HfstTransducer.read_from_file(str(dst))
    assert [o for o, _w in back.lookup("a")] == ["b"]
