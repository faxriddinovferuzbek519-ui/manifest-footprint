"""Read dependency declarations from common project manifest files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from packaging.requirements import InvalidRequirement, Requirement


@dataclass(frozen=True)
class Dependency:
    """A dependency declaration found in a manifest."""

    ecosystem: str
    name: str
    declared: str
    manifest: str
    group: str = "dependencies"


@dataclass(frozen=True)
class ParseResult:
    dependencies: tuple[Dependency, ...]
    warnings: tuple[str, ...] = ()


def parse_requirements_file(path: Path) -> ParseResult:
    """Parse simple PEP 508 entries from a requirements.txt file.

    Options, nested requirement files, and editable/VCS installs are not resolved in
    this first version. They are skipped with a warning rather than guessed at.
    """

    dependencies: list[Dependency] = []
    warnings: list[str] = []

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return ParseResult((), (f"Could not read {path}: {exc}",))

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-", "--")):
            warnings.append(
                f"{path}:{line_number}: skipped requirements option or include: {line}"
            )
            continue

        try:
            requirement = Requirement(line)
        except InvalidRequirement:
            warnings.append(f"{path}:{line_number}: could not parse requirement: {line}")
            continue

        if requirement.url:
            warnings.append(
                f"{path}:{line_number}: skipped direct URL dependency: {requirement.name}"
            )
            continue

        dependencies.append(
            Dependency(
                ecosystem="pypi",
                name=requirement.name,
                declared=str(requirement.specifier) or "(not specified)",
                manifest=str(path),
                group="dependencies",
            )
        )

    return ParseResult(tuple(dependencies), tuple(warnings))


def parse_package_json(path: Path) -> ParseResult:
    """Read dependencies from package.json dependency sections."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ParseResult((), (f"Could not read valid JSON from {path}: {exc}",))

    if not isinstance(payload, dict):
        return ParseResult((), (f"{path}: expected a JSON object at the top level",))

    sections = (
        "dependencies",
        "devDependencies",
        "optionalDependencies",
        "peerDependencies",
    )
    dependencies: list[Dependency] = []
    warnings: list[str] = []

    for section in sections:
        values = payload.get(section, {})
        if values is None:
            continue
        if not isinstance(values, dict):
            warnings.append(f"{path}: {section} should be a JSON object; skipped it")
            continue
        for name, declared in values.items():
            if not isinstance(name, str) or not isinstance(declared, str):
                warnings.append(f"{path}: ignored an invalid entry in {section}")
                continue
            dependencies.append(
                Dependency(
                    ecosystem="npm",
                    name=name,
                    declared=declared,
                    manifest=str(path),
                    group=section,
                )
            )

    return ParseResult(tuple(dependencies), tuple(warnings))


def discover_manifests(target: Path) -> tuple[Path, ...]:
    """Find supported manifests at the target path or its top level."""

    if target.is_file():
        if target.name in {"requirements.txt", "package.json"}:
            return (target,)
        return ()

    if not target.is_dir():
        return ()

    candidates = (target / "requirements.txt", target / "package.json")
    return tuple(candidate for candidate in candidates if candidate.is_file())


def parse_manifests(paths: Iterable[Path]) -> ParseResult:
    """Parse all supplied manifest paths and combine their results."""

    dependencies: list[Dependency] = []
    warnings: list[str] = []
    seen: set[tuple[str, str, str, str]] = set()

    for path in paths:
        result = (
            parse_requirements_file(path)
            if path.name == "requirements.txt"
            else parse_package_json(path)
        )
        warnings.extend(result.warnings)
        for dependency in result.dependencies:
            key = (
                dependency.ecosystem,
                dependency.name.lower(),
                dependency.declared,
                dependency.group,
            )
            if key not in seen:
                seen.add(key)
                dependencies.append(dependency)

    return ParseResult(tuple(dependencies), tuple(warnings))
