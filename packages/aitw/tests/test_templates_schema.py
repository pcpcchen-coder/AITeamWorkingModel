"""WP-001 AC6：11 §4 各檔案的 JSON Schema 存在；kit/templates/ 全部樣板通過 schema。"""

from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator

from aitw import frontmatter, schemas, yamlio
from conftest import REPO_ROOT

TEMPLATES = REPO_ROOT / "kit" / "templates"

# 每個樣板對應的 schema；新增樣板時必須在此登錄（下方測試會擋下漏登錄者）。
TEMPLATE_SCHEMA = {
    "config.yaml": "config",
    "decision-request.md": "decision-request",
    "evidence-manifest.yaml": "evidence-manifest",
    "human-task-record.md": "human-task-record",
    "mission.md": "mission",
    "policy.yaml": "policy",
    "review-packet.md": "review-packet",
    "sync-agenda.md": "sync-agenda",
    "takeover-package.md": "takeover-package",
    "verification-report.md": "verification-report",
    "weekly-digest.md": "weekly-digest",
    "wp.md": "wp",
}

# docs/11 §4.1–§4.5 列出的檔案種類（加上 knowledge/requirements.yaml）
SPEC_FILE_KINDS = {"wp", "evidence-manifest", "review-packet", "decision-request", "mission",
                   "human-task-record", "config", "policy", "weekly-digest", "sync-agenda",
                   "takeover-package", "verification-report", "requirements"}


@pytest.mark.wp001_ac6
def test_every_spec_file_kind_has_a_schema():
    assert SPEC_FILE_KINDS <= set(schemas.SCHEMA_NAMES)


@pytest.mark.wp001_ac6
@pytest.mark.parametrize("name", schemas.SCHEMA_NAMES)
def test_schema_is_valid_draft_2020_12(name):
    schema = schemas.load_schema(name)
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema.get("x-doc"), "每個 schema 需指出規格出處（x-doc）"


@pytest.mark.wp001_ac6
def test_every_template_is_mapped_to_a_schema():
    present = {p.name for p in TEMPLATES.iterdir() if p.is_file()}
    assert present == set(TEMPLATE_SCHEMA), f"未登錄或已移除的樣板：{present ^ set(TEMPLATE_SCHEMA)}"


@pytest.mark.wp001_ac6
@pytest.mark.parametrize("template", sorted(TEMPLATE_SCHEMA))
def test_template_passes_schema(template):
    text = (TEMPLATES / template).read_text(encoding="utf-8")
    if template.endswith(".md"):
        text = frontmatter.split(text).front_matter
    data = yamlio.load(text)
    errors = sorted(schemas.validator(TEMPLATE_SCHEMA[template]).iter_errors(data), key=str)
    assert not errors, "\n".join(f"{list(e.absolute_path)}: {e.message}" for e in errors)


@pytest.mark.wp001_ac6
@pytest.mark.parametrize("bad, schema", [
    ({"wp": "WP-001", "items": [{"id": "EV-001-01", "ac": "AC1", "kind": "test_run",
                                 "produced_by": "agent:x", "label": "OBSERVED"}]}, "evidence-manifest"),
    ({"wp": "WP-001", "items": [{"id": "EV-001-01", "ac": "AC1", "kind": "measurement",
                                 "produced_by": "human:x", "label": "OBSERVED"}]}, "evidence-manifest"),
])
def test_kind_specific_required_fields_are_enforced(bad, schema):
    """DR-P3：指令類證據需執行欄位；量測類需 conditions／outputs。"""
    assert list(schemas.validator(schema).iter_errors(bad))
