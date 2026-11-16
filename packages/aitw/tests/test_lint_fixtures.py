"""WP-001 AC2：刻意寫壞的 fixture 各自失敗，訊息含檔案、欄位、原因、修正方式。

每個案例複製虛構的 valid-minimal 專案，只改一處，然後斷言：
  * 結束碼為 1（交叉引用／schema）或 2（YAML／front matter 格式錯誤）；
  * 文字輸出含該檔案路徑、欄位、原因與修正四行；
  * JSON 輸出中有對應 code 與欄位的問題。
所有資料皆為虛構測試資料（fictional test data）。
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

from conftest import lint_json, run_lint

M = "work/missions/M-001-demo"
WP1 = f"{M}/wp/WP-001-alpha"
WP2 = f"{M}/wp/WP-002-beta"


def _replace(repo: Path, rel: str, old: str, new: str) -> None:
    p = repo / rel
    text = p.read_text(encoding="utf-8")
    assert old in text, f"fixture mutation anchor not found in {rel}: {old!r}"
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def _copy_wp(repo: Path, src: str, dst: str) -> None:
    shutil.copytree(repo / src, repo / dst)


@dataclass(frozen=True)
class Case:
    id: str
    mutate: Callable[[Path], None]
    file: str
    field: str
    code: str
    exit_code: int = 1


CASES = [
    # --- docs/13 K0 明列的六類 ---
    Case("missing_required_field",
         lambda r: _replace(r, f"{WP1}/wp.md", "title: 虛構工作包：換算函式\n", ""),
         f"{WP1}/wp.md", "-", "schema.required"),
    Case("duplicate_wp_id",
         lambda r: (_copy_wp(r, WP2, f"{M}/wp/WP-003-gamma"),
                    _replace(r, f"{M}/wp/WP-003-gamma/wp.md", "id: WP-002", "id: WP-003"),
                    _replace(r, f"{M}/wp/WP-003-gamma/wp.md", "id: WP-003", "id: WP-002")),
         f"{M}/wp/WP-003-gamma/wp.md", "id", "id.duplicate"),
    Case("depends_on_missing_wp",
         lambda r: _replace(r, f"{WP2}/wp.md", "depends_on: [WP-001]", "depends_on: [WP-099]"),
         f"{WP2}/wp.md", "depends_on[0]", "ref.wp"),
    Case("unknown_enum_value",
         lambda r: _replace(r, f"{WP1}/wp.md", "domain: sw", "domain: firmware"),
         f"{WP1}/wp.md", "domain", "schema.enum"),
    Case("acceptance_missing_verify",
         lambda r: _replace(r, f"{WP2}/wp.md",
                            '    verify: {kind: test_run, runner: ci, command: "python -m pytest sw/app", ladder: V3}\n',
                            ""),
         f"{WP2}/wp.md", "acceptance[0]", "schema.required"),
    Case("dependency_cycle",
         lambda r: _replace(r, f"{WP1}/wp.md", "depends_on: []", "depends_on: [WP-002]"),
         f"{WP1}/wp.md", "depends_on", "wp.dependency_cycle"),
    # --- 其他常見錯誤 ---
    Case("ci_runner_without_command",
         lambda r: _replace(r, f"{WP2}/wp.md", ', command: "python -m pytest sw/app"', ""),
         f"{WP2}/wp.md", "acceptance[0].verify", "schema.required"),
    Case("wp_references_missing_mission",
         lambda r: _replace(r, f"{WP2}/wp.md", "mission: M-001", "mission: M-009"),
         f"{WP2}/wp.md", "mission", "ref.mission"),
    Case("evidence_references_missing_ac",
         lambda r: _replace(r, f"{WP1}/evidence/manifest.yaml", "ac: AC1", "ac: AC9"),
         f"{WP1}/evidence/manifest.yaml", "items[0].ac", "ref.acceptance"),
    Case("invalid_id_pattern",
         lambda r: _replace(r, f"{WP2}/wp.md", "id: WP-002", "id: WP-2"),
         f"{WP2}/wp.md", "id", "schema.pattern"),
    Case("satisfies_unknown_requirement",
         lambda r: _replace(r, f"{WP1}/wp.md", "satisfies: [REQ-001]", "satisfies: [REQ-099]"),
         f"{WP1}/wp.md", "satisfies[0]", "ref.requirement"),
    Case("unfilled_placeholder",
         lambda r: _replace(r, f"{M}/mission.md", "owner: primary-a", "owner: <primary 的 forge 帳號>"),
         f"{M}/mission.md", "owner", "template.placeholder"),
    Case("g3_without_start_approval",
         lambda r: (_replace(r, f"{WP2}/wp.md", "gate: G1", "gate: G3"),
                    _replace(r, f"{WP2}/wp.md", "autonomy: A2", "autonomy: A0"),
                    _replace(r, f"{WP2}/wp.md", "executor: ai", "executor: pair"),
                    _replace(r, f"{WP2}/wp.md", "review_tier: R2", "review_tier: R3")),
         f"{WP2}/wp.md", "start_approval", "schema.const"),
    Case("autonomy_gate_incompatible",
         lambda r: (_replace(r, f"{WP1}/wp.md", "autonomy: A2", "autonomy: A3"),   # A3 只允許 G0／G1
                    _replace(r, f"{WP1}/wp.md", "gate: G1", "gate: G2")),
         f"{WP1}/wp.md", "gate", "wp.autonomy_gate"),
    Case("review_tier_below_gate_default",
         lambda r: _replace(r, f"{WP1}/wp.md", "review_tier: R2", "review_tier: R1"),
         f"{WP1}/wp.md", "review_tier", "wp.review_tier"),
    Case("wp_dir_name_mismatch",
         lambda r: (r / WP2).rename(r / f"{M}/wp/WP-007-beta"),
         f"{M}/wp/WP-007-beta/wp.md", "id", "wp.dir_mismatch"),
    Case("decision_blocks_missing_wp",
         lambda r: _replace(r, f"{WP1}/decisions/DR-001.md", "blocks: [WP-002]", "blocks: [WP-042]"),
         f"{WP1}/decisions/DR-001.md", "blocks[0]", "ref.wp"),
    Case("packet_claim_missing_evidence",
         lambda r: _replace(r, f"{WP1}/review/packet-r1.md", "evidence: [EV-001-01]", "evidence: [EV-001-07]"),
         f"{WP1}/review/packet-r1.md", "claims[0].evidence[0]", "ref.evidence"),
    Case("unknown_field_typo",
         lambda r: _replace(r, f"{WP2}/wp.md", "acceptance:", "acceptence: []\nacceptance:"),
         f"{WP2}/wp.md", "-", "schema.unknown_field"),
    # --- 格式錯誤（結束碼 2）---
    Case("duplicate_yaml_key",
         lambda r: _replace(r, f"{WP2}/wp.md", "gate: G1", "gate: G1\ngate: G2"),
         f"{WP2}/wp.md", "gate", "yaml.duplicate_key", exit_code=2),
    Case("missing_front_matter",
         lambda r: _replace(r, f"{M}/mission.md", "---\n# 虛構", "# 虛構"),
         f"{M}/mission.md", "-", "file.front_matter", exit_code=2),
]


@pytest.mark.wp001_ac2
def test_at_least_eight_broken_fixtures():
    assert len(CASES) >= 8
    assert len({c.id for c in CASES}) == len(CASES)


@pytest.mark.wp001_ac2
def test_valid_fixture_passes(valid_repo, capsys):
    code, out = run_lint(valid_repo, capsys)
    assert code == 0, out
    assert "通過" in out


@pytest.mark.wp001_ac2
@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
def test_broken_fixture_fails_with_actionable_message(case: Case, valid_repo, capsys):
    case.mutate(valid_repo)

    code, out = run_lint(valid_repo, capsys)
    assert code == case.exit_code, out
    # 文字輸出：檔案、欄位、原因、修正方式四項都要有
    assert f"✘ {case.file}" in out, out
    assert f"  欄位：{case.field}" in out, out
    assert "  原因：" in out and "  修正：" in out, out

    code_j, data = lint_json(valid_repo, capsys)
    assert code_j == case.exit_code
    assert data["ok"] is False
    hits = [i for i in data["issues"] if i["code"] == case.code and i["file"] == case.file]
    assert hits, data["issues"]
    assert any(h["field"] == case.field for h in hits), hits
    for h in hits:
        assert h["reason"].strip() and h["fix"].strip()
