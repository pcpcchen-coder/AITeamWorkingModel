"""不變量 I1：CLI 不呼叫任何模型；相同輸入產生相同輸出。"""

from __future__ import annotations

import ast
import socket
import tomllib

import pytest

from conftest import FIXTURES, REPO_ROOT, run_lint

PKG = REPO_ROOT / "packages" / "aitw"
MODEL_SDKS = {"anthropic", "openai", "google", "googleapiclient", "vertexai", "cohere", "mistralai",
              "ollama", "langchain", "llama_index", "transformers", "litellm", "groq", "together"}
ALLOWED_RUNTIME_DEPS = {"pyyaml", "jsonschema"}


@pytest.mark.inv_i1
@pytest.mark.parametrize("json_out", [False, True], ids=["text", "json"])
def test_lint_output_is_byte_identical_across_runs(valid_repo, capsys, json_out):
    (valid_repo / "work/missions/M-001-demo/wp/WP-002-beta/wp.md").write_text(
        "---\nid: WP-2\n---\n", encoding="utf-8")  # 加入錯誤，確保比較的是非空輸出
    first = run_lint(valid_repo, capsys, json_out)
    for _ in range(3):
        assert run_lint(valid_repo, capsys, json_out) == first
    assert first[0] != 0 and first[1]


@pytest.mark.inv_i1
def test_lint_output_does_not_depend_on_repo_location(tmp_path, capsys):
    import shutil
    a, b = tmp_path / "a" / "repo", tmp_path / "b" / "nested" / "repo"
    shutil.copytree(FIXTURES / "valid-minimal", a)
    shutil.copytree(FIXTURES / "valid-minimal", b)
    assert run_lint(a, capsys, True) == run_lint(b, capsys, True)


@pytest.mark.inv_i1
def test_runtime_dependencies_contain_no_model_sdk():
    meta = tomllib.loads((PKG / "pyproject.toml").read_text(encoding="utf-8"))
    deps = {d.split(">")[0].split("=")[0].split("[")[0].strip().lower() for d in meta["project"]["dependencies"]}
    assert deps == ALLOWED_RUNTIME_DEPS, f"新增執行期相依需在 PR 說明必要性：{deps - ALLOWED_RUNTIME_DEPS}"
    assert not deps & MODEL_SDKS


@pytest.mark.inv_i1
def test_source_imports_no_model_sdk_or_network_client():
    forbidden = MODEL_SDKS | {"requests", "httpx", "urllib3", "aiohttp", "socket", "http"}
    for path in sorted((PKG / "src" / "aitw").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            for n in names:
                top = n.split(".")[0]
                assert top not in forbidden, f"{path.relative_to(REPO_ROOT)} imports {n}"
                assert not (top == "urllib" and n.startswith("urllib.request")), path


@pytest.mark.inv_i1
def test_network_is_blocked_during_tests():
    with pytest.raises(RuntimeError, match="network access is forbidden"):
        socket.create_connection(("example.invalid", 443), timeout=1)
