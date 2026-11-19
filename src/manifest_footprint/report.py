"""Render scan results for terminals and Markdown files."""

from __future__ import annotations

import json


def render_json(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Manifest Footprint report",
        "",
        f"Scanned: `{report['target']}`",
        "",
        "## Summary",
        "",
        "| Checked | Outdated | Current | Review | Errors |",
        "| ---: | ---: | ---: | ---: | ---: |",
        "| {checked} | {outdated} | {current} | {review} | {errors} |".format(**summary),
        "",
        "## Dependencies",
        "",
        "| Package | Ecosystem | Declared | Latest | Status | Manifest group |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    if report["findings"]:
        for item in report["findings"]:
            values = [
                item["name"],
                item["ecosystem"],
                item["declared"],
                item["latest"] or "—",
                item["status"],
                item["group"],
            ]
            lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    else:
        lines.append("| No dependencies found | — | — | — | — | — |")

    if report["findings"]:
        lines.extend(["", "## Details", ""])
        for item in report["findings"]:
            lines.append(f"- **{item['name']}** ({item['status']}): {item['detail']}")
            if item["registry_url"]:
                lines.append(f"  Registry: {item['registry_url']}")

    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])

    lines.extend(
        [
            "",
            "> This report checks public registry metadata. It does not inspect installed "
            "packages, security advisories, licenses, or transitive dependencies.",
            "",
        ]
    )
    return "\n".join(lines)


def render_text(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "Manifest Footprint",
        f"Target: {report['target']}",
        (
            "Checked: {checked} | Outdated: {outdated} | Current: {current} | "
            "Review: {review} | Errors: {errors}"
        ).format(**summary),
        "",
    ]
    for item in report["findings"]:
        latest = item["latest"] or "unknown"
        lines.append(
            f"[{item['status'].upper():8}] {item['ecosystem']:4} "
            f"{item['name']} ({item['declared']}) -> {latest}"
        )
        lines.append(f"           {item['detail']}")
    if not report["findings"]:
        lines.append("No dependencies found in supported manifests.")
    for warning in report["warnings"]:
        lines.append(f"WARNING: {warning}")
    return "\n".join(lines)
