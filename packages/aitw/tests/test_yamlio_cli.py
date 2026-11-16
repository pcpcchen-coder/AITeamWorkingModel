"""嚴格 YAML 載入器與 CLI 基本行為的單元測試（虛構測試資料）。"""

from __future__ import annotations

import subprocess
import sys

import pytest

from aitw import frontmatter, yamlio
from aitw.cli import main
from conftest import REPO_ROOT


def test_dates_stay_strings():
    assert yamlio.load("needed_by: 2026-11-18") == {"needed_by": "2026-11-18"}


def test_yaml11_booleans_are_not_booleans():
    assert yamlio.load("a: no\nb: on\nc: true\nd: False") == {"a": "no", "b": "on", "c": True, "d": False}


def test_duplicate_keys_rejected():
    with pytest.raises(yamlio.DuplicateKeyError):
        yamlio.load("a: 1\na: 2\n")


def test_unsafe_tags_rejected():
    import yaml
    with pytest.raises(yaml.YAMLError):
        yamlio.load("x: !!python/object/apply:os.system ['true']")


def test_front_matter_split():
    doc = frontmatter.split("---\nid: X\n---\n\nbody\n")
    assert doc.front_matter == "id: X\n" and doc.body == "\nbody\n" and doc.body_start_line == 4


@pytest.mark.parametrize("text", ["no front matter\n", "---\nid: X\n"])
def test_front_matter_errors(text):
    with pytest.raises(frontmatter.FrontMatterError):
        frontmatter.split(text)


def test_missing_repo_is_usage_error(tmp_path, capsys):
    assert main(["--repo", str(tmp_path / "nope"), "lint"]) == 2
    assert "修正" in capsys.readouterr().err


def test_unknown_command_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["frobnicate"])
    assert exc.value.code == 2


def test_module_entry_point_runs(tmp_path):
    env_path = str(REPO_ROOT / "packages" / "aitw" / "src")
    proc = subprocess.run([sys.executable, "-m", "aitw", "--repo", str(tmp_path), "lint"],
                          capture_output=True, text=True, timeout=60,
                          env={"PYTHONPATH": env_path, "PATH": ""})
    assert proc.returncode == 0, proc.stderr
    assert "通過" in proc.stdout
