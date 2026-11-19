"""Dependency checking and report assembly."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from packaging.version import InvalidVersion, Version

from .parsers import Dependency, discover_manifests, parse_manifests
from .registry import RegistryError, latest_version


@dataclass(frozen=True)
class Finding:
    ecosystem: str
    name: str
    declared: str
    latest: str | None
    status: str
    manifest: str
    group: str
    registry_url: str | None = None
    detail: str = ""


def _python_pin(declared: str) -> str | None:
    """Return an exact PEP 440 pin when the declaration is one simple == pin."""

    match = re.fullmatch(r"\s*==\s*([A-Za-z0-9.!+_-]+)\s*", declared)
    if not match or "*" in match.group(1):
        return None
    return match.group(1)


def _npm_pin(declared: str) -> str | None:
    """Return a plain stable x.y.z npm pin; ranges need a full semver evaluator."""

    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", declared.strip())
    return ".".join(match.groups()) if match else None


def classify(dependency: Dependency, latest: str) -> tuple[str, str]:
    """Classify what can safely be concluded from a declaration and latest version."""

    if dependency.ecosystem == "pypi":
        pin = _python_pin(dependency.declared)
        if pin is None:
            return (
                "review",
                "Latest release found. This declaration is not a single exact pin, "
                "so it cannot be compared reliably without a lockfile.",
            )
        try:
            is_outdated = Version(latest) > Version(pin)
        except InvalidVersion:
            return "review", "Could not compare the declared and latest versions safely."
        if is_outdated:
            return "outdated", f"A newer release is available than the pinned version {pin}."
        return "current", "The exact pinned version is not older than the registry's latest version."

    if dependency.ecosystem == "npm":
        pin = _npm_pin(dependency.declared)
        latest_match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", latest)
        if pin is None or latest_match is None:
            return (
                "review",
                "Latest release found. The declared npm range was not evaluated; "
                "range compatibility needs a SemVer-aware check.",
            )
        pin_tuple = tuple(int(part) for part in pin.split("."))
        latest_tuple = tuple(int(part) for part in latest_match.groups())
        if latest_tuple > pin_tuple:
            return "outdated", f"A newer release is available than the exact version {pin}."
        return "current", "The exact pinned version is not older than the registry's latest version."

    return "review", "No comparison rule is available for this ecosystem."


def check_dependency(
    dependency: Dependency,
    timeout: float = 8.0,
    version_lookup: Callable[[str, str, float], tuple[str, str]] = latest_version,
) -> Finding:
    """Check one dependency; registry errors become findings instead of stopping the scan."""

    try:
        latest, registry_url = version_lookup(dependency.ecosystem, dependency.name, timeout)
        status, detail = classify(dependency, latest)
        return Finding(
            ecosystem=dependency.ecosystem,
            name=dependency.name,
            declared=dependency.declared,
            latest=latest,
            status=status,
            manifest=dependency.manifest,
            group=dependency.group,
            registry_url=registry_url,
            detail=detail,
        )
    except (RegistryError, OSError, ValueError) as exc:
        return Finding(
            ecosystem=dependency.ecosystem,
            name=dependency.name,
            declared=dependency.declared,
            latest=None,
            status="error",
            manifest=dependency.manifest,
            group=dependency.group,
            detail=f"Could not check registry metadata: {exc}",
        )


def scan(target: Path, timeout: float = 8.0) -> dict:
    """Scan a directory or one supported manifest and return a JSON-ready report."""

    target = target.expanduser().resolve()
    manifests = discover_manifests(target)
    parsed = parse_manifests(manifests)
    findings = [asdict(check_dependency(item, timeout=timeout)) for item in parsed.dependencies]
    statuses = [item["status"] for item in findings]

    return {
        "tool": "manifest-footprint",
        "version": "0.1.0",
        "target": str(target),
        "manifests": [str(path) for path in manifests],
        "summary": {
            "checked": len(findings),
            "outdated": statuses.count("outdated"),
            "current": statuses.count("current"),
            "review": statuses.count("review"),
            "errors": statuses.count("error"),
        },
        "warnings": list(parsed.warnings),
        "findings": findings,
    }
