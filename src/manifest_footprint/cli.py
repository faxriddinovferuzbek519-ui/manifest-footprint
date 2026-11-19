"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import render_json, render_markdown, render_text
from .scanner import scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manifest-footprint",
        description="Check declared Python and JavaScript dependencies against public registries.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="project directory or a requirements.txt/package.json file (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="report format (default: text)",
    )
    parser.add_argument("--output", help="write the report to a file instead of the terminal")
    parser.add_argument(
        "--timeout",
        type=float,
        default=8.0,
        help="timeout in seconds for each registry request (default: 8)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")

    target = Path(args.path)
    if not target.exists():
        parser.error(f"path does not exist: {target}")

    report = scan(target, timeout=args.timeout)
    renderers = {"text": render_text, "markdown": render_markdown, "json": render_json}
    output = renderers[args.format](report)

    if args.output:
        try:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Could not write report: {exc}", file=sys.stderr)
            return 2
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
