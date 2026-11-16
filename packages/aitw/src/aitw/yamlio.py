"""Deterministic, strict YAML loading.

PyYAML's default (YAML 1.1) resolvers turn ``2026-11-18`` into a ``date`` and
``no``/``on`` into booleans, and silently keep the last of duplicated keys.
All three would make file contracts ambiguous, so this loader:

* keeps timestamps as plain strings;
* only treats ``true``/``false`` (any case) as booleans;
* rejects duplicate mapping keys.
"""

from __future__ import annotations

import re

import yaml


class DuplicateKeyError(yaml.constructor.ConstructorError):
    """Raised when a mapping contains the same key twice."""


class StrictLoader(yaml.SafeLoader):
    """SafeLoader with stricter, YAML-1.2-like scalar resolution."""


# Rebuild implicit resolvers without timestamp and YAML 1.1 booleans.
StrictLoader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag not in (
        "tag:yaml.org,2002:timestamp",
        "tag:yaml.org,2002:bool",
    )]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
StrictLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


def _construct_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load(text: str):
    """Parse one YAML document strictly. Raises ``yaml.YAMLError`` on failure."""
    return yaml.load(text, Loader=StrictLoader)  # noqa: S506 - StrictLoader derives from SafeLoader
