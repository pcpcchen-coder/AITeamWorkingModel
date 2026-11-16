"""Split a Markdown file into YAML front matter and body."""

from __future__ import annotations

from dataclasses import dataclass


class FrontMatterError(ValueError):
    """The file does not start with a ``---`` delimited YAML block."""


@dataclass(frozen=True)
class Document:
    front_matter: str
    body: str
    body_start_line: int  # 1-based line number where the body begins


def split(text: str) -> Document:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise FrontMatterError("檔案開頭不是 '---'，找不到 YAML front matter")
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == "---":
            return Document(
                front_matter="".join(lines[1:idx]),
                body="".join(lines[idx + 1 :]),
                body_start_line=idx + 2,
            )
    raise FrontMatterError("找不到結尾的 '---'，front matter 未關閉")
