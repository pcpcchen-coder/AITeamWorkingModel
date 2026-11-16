"""Access to the bundled JSON Schemas (docs/11 §4)."""

from __future__ import annotations

import json
from functools import cache
from importlib import resources

from jsonschema import Draft202012Validator

SCHEMA_NAMES = (
    "config",
    "decision-request",
    "evidence-manifest",
    "human-task-record",
    "mission",
    "policy",
    "requirements",
    "review-packet",
    "sync-agenda",
    "takeover-package",
    "verification-report",
    "weekly-digest",
    "wp",
)


@cache
def load_schema(name: str) -> dict:
    if name not in SCHEMA_NAMES:
        raise KeyError(f"unknown schema: {name}")
    text = resources.files("aitw").joinpath("schemas", f"{name}.schema.json").read_text(encoding="utf-8")
    return json.loads(text)


@cache
def validator(name: str) -> Draft202012Validator:
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)
