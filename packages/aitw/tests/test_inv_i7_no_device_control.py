"""不變量 I7：工具不含、也不產生任何燒錄、除錯器、儀器或設備控制指令。

掃描範圍：packages/aitw/src、kit/、examples/，以及 CLI 的實際輸出。
例外（DR-P6）：K4 的拒絕清單資料檔必須列出這些工具名稱作為攔截樣式；
這類檔案必須逐一明列於 DENYLIST_DATA_FILES，變更即列入必看清單。
"""

from __future__ import annotations

import re

import pytest

from conftest import FIXTURES, REPO_ROOT, run_lint

SCAN_ROOTS = ["packages/aitw/src", "kit", "examples"]
DENYLIST_DATA_FILES: set[str] = set()  # K4（WP-006）加入時逐一列名

PATTERNS = [
    # 燒錄／除錯連線工具
    r"\bopenocd\b", r"\bst-flash\b", r"\bst-util\b", r"\bstm32_programmer_cli\b", r"\bstm32cubeprogrammer\b",
    r"\bjlink(?:exe|gdbserver)?\b", r"\bnrfjprog\b", r"\besptool(?:\.py)?\b", r"\bavrdude\b", r"\bpyocd\b",
    r"\bdfu-util\b", r"\bprobe-rs\b", r"\bpicotool\b", r"\bbossac\b", r"\bteensy_loader_cli\b", r"\bflashrom\b",
    r"\btarget\s+(?:extended-)?remote\b", r"\bmonitor\s+(?:reset|halt|flash)\b",
    # 串列埠與儀器匯流排
    r"/dev/tty(?:USB|ACM|S)\d*", r"\bminicom\b", r"\bpicocom\b", r"\bserial\.Serial\s*\(", r"\bpyserial\b",
    r"\bpyvisa\b", r"\*IDN\?", r"\bTCPIP0::", r"\bGPIB\d*::",
]
RX = re.compile("|".join(PATTERNS), re.IGNORECASE)
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".c", ".h", ".mk", ".cfg",
                 ".ini", ".html", ""}


def _scan_text(text: str) -> list[str]:
    return [m.group(0) for m in RX.finditer(text)]


def _files():
    for root in SCAN_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and (p.suffix.lower() in TEXT_SUFFIXES or p.name == "Makefile"):
                rel = p.relative_to(REPO_ROOT).as_posix()
                if rel not in DENYLIST_DATA_FILES and "__pycache__" not in rel:
                    yield rel, p


@pytest.mark.inv_i7
def test_scanner_detects_planted_command():
    planted = "run: " + "open" + "ocd -f board.cfg -c 'program fw.elf'\n" + "rm = py" + "visa.ResourceManager()"
    assert len(_scan_text(planted)) == 2


@pytest.mark.inv_i7
def test_scanner_ignores_ordinary_words():
    assert _scan_text("燒錄由人執行；人類任務（量測、燒錄）只由合格人員操作。flash usage report; serial number") == []


@pytest.mark.inv_i7
def test_tool_sources_kit_and_examples_contain_no_device_control():
    hits = {}
    for rel, path in _files():
        found = _scan_text(path.read_text(encoding="utf-8", errors="replace"))
        if found:
            hits[rel] = found
    assert not hits, f"發現設備控制相關指令：{hits}"


@pytest.mark.inv_i7
def test_cli_output_contains_no_device_control(tmp_path, capsys):
    import shutil
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURES / "valid-minimal", repo)
    for json_out in (False, True):
        _, out = run_lint(repo, capsys, json_out)
        assert _scan_text(out) == []
    _, out = run_lint(REPO_ROOT, capsys, True)
    assert _scan_text(out) == []
