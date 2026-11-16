"""Check a MicroPython source file without importing or running it.

VS Code passes its active editor path here. Parsing on the computer catches
ordinary Python syntax errors before a script is sent to the board; hardware
imports and device-only APIs are intentionally left untouched.
"""

import ast
import sys
from pathlib import Path


def main() -> int:
    """Read the selected source and report a useful location on syntax errors."""
    if len(sys.argv) != 2:
        print("用法: python check_syntax.py <MicroPython脚本路径>", file=sys.stderr)
        return 2

    source_path = Path(sys.argv[1])
    if not source_path.is_file():
        print(f"文件不存在: {source_path}", file=sys.stderr)
        return 2

    try:
        ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    except (SyntaxError, UnicodeError) as error:
        print(f"语法检查失败: {error}", file=sys.stderr)
        return 1

    print(f"语法检查通过: {source_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
