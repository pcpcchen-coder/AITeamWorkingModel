"""不變量 I8：所有範例與測試資料皆為虛構並如此標示；不含 secret、真實量測或內部資訊。

規則：examples/ 與測試 fixture 底下的每個檔案，必須本身含「虛構」或「fictional」字樣，
或其所在目錄有含此字樣的 README.md／FICTIONAL.md。另以樣式掃描全 repo 的 secret。
「真實量測或內部資訊」無法以程式完全判定，仍需人類審閱（PR 必看清單）。
"""

from __future__ import annotations

import re

import pytest

from conftest import FIXTURES, REPO_ROOT

DATA_ROOTS = [REPO_ROOT / "examples", FIXTURES]
MARKER = re.compile(r"虛構|fictional", re.IGNORECASE)
NOTE_FILES = ("README.md", "FICTIONAL.md")

SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",
    r"\bgh[pousr]_[A-Za-z0-9]{36,}",
    r"\bgithub_pat_[A-Za-z0-9_]{22,}",
    r"\bglpat-[A-Za-z0-9_\-]{20,}",
    r"\bxox[baprs]-[A-Za-z0-9-]{10,}",
    r"\bsk-ant-[A-Za-z0-9_\-]{20,}",
    r"\bsk-[A-Za-z0-9]{32,}",
    r"\bAIza[0-9A-Za-z_\-]{35}",
]
SECRET_RX = re.compile("|".join(SECRET_PATTERNS))
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", ".venv"}


def _dir_has_note(directory) -> bool:
    for name in NOTE_FILES:
        note = directory / name
        if note.is_file() and MARKER.search(note.read_text(encoding="utf-8", errors="replace")):
            return True
    return False


def _data_files():
    for root in DATA_ROOTS:
        if root.exists():
            for p in sorted(root.rglob("*")):
                if p.is_file() and not (set(p.relative_to(REPO_ROOT).parts) & SKIP_DIRS):
                    yield p


@pytest.mark.inv_i8
def test_every_example_and_fixture_file_is_marked_fictional():
    unmarked = []
    for p in _data_files():
        text = p.read_text(encoding="utf-8", errors="replace")
        if not MARKER.search(text) and not _dir_has_note(p.parent):
            unmarked.append(p.relative_to(REPO_ROOT).as_posix())
    assert not unmarked, f"未標示為虛構的範例／測試資料：{unmarked}"


@pytest.mark.inv_i8
def test_secret_scanner_detects_planted_samples():
    samples = ["AKIA" + "ABCDEFGHIJKLMNOP", "-----BEGIN " + "PRIVATE KEY-----", "ghp_" + "a" * 36,
               "glpat-" + "b" * 20, "sk-ant-" + "c" * 24]
    for s in samples:
        assert SECRET_RX.search(s), s


@pytest.mark.inv_i8
def test_repository_contains_no_secret_patterns():
    hits = []
    for p in sorted(REPO_ROOT.rglob("*")):
        if not p.is_file() or set(p.relative_to(REPO_ROOT).parts) & SKIP_DIRS:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for m in SECRET_RX.finditer(text):
            hits.append(f"{p.relative_to(REPO_ROOT).as_posix()}: {m.group(0)[:12]}…")
    assert not hits, f"疑似 secret：{hits}"
