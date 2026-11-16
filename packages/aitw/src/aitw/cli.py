"""``aitw`` command-line entry point (docs/11 §6).

Exit codes: 0 success · 1 check failed · 2 usage or file-format error ·
3 external dependency unavailable · 4 HALT in effect.
This CLI never calls a language model (invariant I1).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .lint import lint_repo

EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2


class _Parser(argparse.ArgumentParser):
    def error(self, message: str):  # usage errors → exit 2 with a fix hint
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"aitw：用法錯誤：{message}\n修正：執行 `aitw --help` 查看可用指令與參數\n")


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(prog="aitw", description="Git-native Operating Kit CLI（確定性，不呼叫任何模型）")
    p.add_argument("--version", action="version", version=f"aitw {__version__}")
    p.add_argument("--repo", default=".", help="專案 repo 根目錄（預設：目前目錄）")
    p.add_argument("--json", action="store_true", help="以 JSON 輸出")
    sub = p.add_subparsers(dest="command", metavar="<command>", parser_class=_Parser)
    sub.add_parser("lint", help="檢查檔案契約（schema 與交叉引用）")
    return p


def _cmd_lint(args) -> int:
    root = Path(args.repo)
    if not root.is_dir():
        print(f"aitw：找不到 repo 目錄：{args.repo}\n修正：以 --repo 指定專案根目錄", file=sys.stderr)
        return EXIT_USAGE
    result = lint_repo(root)
    if args.json:
        payload = {"ok": result.ok, "files_checked": result.files_checked,
                   "issues": [i.as_dict() for i in result.issues]}
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for issue in result.issues:
            print(f"✘ {issue.file}")
            print(f"  欄位：{issue.field}")
            print(f"  原因：{issue.reason}")
            print(f"  修正：{issue.fix}")
            print(f"  代碼：{issue.code}")
        status = "通過" if result.ok else f"未通過（{len(result.issues)} 個問題）"
        print(f"aitw lint：檢查 {result.files_checked} 個檔案，{status}")
    return result.exit_code


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "lint":
        return _cmd_lint(args)
    build_parser().print_help()
    return EXIT_USAGE


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
