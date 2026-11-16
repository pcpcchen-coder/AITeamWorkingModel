"""Shared test helpers. 所有 fixture 皆為虛構測試資料（fictional test data）。"""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path

import pytest

from aitw.cli import main

TESTS_DIR = Path(__file__).resolve().parent
FIXTURES = TESTS_DIR / "fixtures"
REPO_ROOT = TESTS_DIR.parents[2]


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """Unit tests must not touch the network (docs/13 §1.3, invariant I1)."""

    def _blocked(*_args, **_kwargs):
        raise RuntimeError("network access is forbidden in unit tests")

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


@pytest.fixture
def valid_repo(tmp_path: Path) -> Path:
    """A fresh copy of the valid minimal fictional repo."""
    dst = tmp_path / "repo"
    shutil.copytree(FIXTURES / "valid-minimal", dst)
    return dst


def run_lint(repo: Path, capsys, json_out: bool = False) -> tuple[int, str]:
    argv = ["--repo", str(repo)] + (["--json"] if json_out else []) + ["lint"]
    code = main(argv)
    out = capsys.readouterr().out
    return code, out


def lint_json(repo: Path, capsys) -> tuple[int, dict]:
    code, out = run_lint(repo, capsys, json_out=True)
    return code, json.loads(out)
