# Manifest Footprint

A small command-line tool that reads `requirements.txt` and `package.json`, looks up the latest public release for each declared package, and creates a dependency report.

The goal is to make dependency information easier to review, especially for small projects that do not have a dedicated dependency monitoring service.

> **Project status:** early MVP. It currently checks direct dependencies in two manifest formats. It is not a security scanner and should not be used as the only input for production dependency decisions.

## What it does

- Reads Python dependencies from a top-level `requirements.txt`.
- Reads JavaScript dependencies from `dependencies`, `devDependencies`, `optionalDependencies`, and `peerDependencies` in `package.json`.
- Looks up package metadata from the public PyPI and npm registries.
- Identifies newer releases for simple exact version pins.
- Marks version ranges for review instead of guessing whether they are outdated.
- Produces terminal, Markdown, or JSON output.

## Requirements

- Python 3.10 or newer
- An internet connection for registry lookups

## Install from a local checkout

```bash
git clone https://github.com/faxriddinovferuzbek519-ui/manifest-footprint.git
cd manifest-footprint
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

python -m pip install -e ".[dev]"
```

## Usage

Scan the current project directory:

```bash
manifest-footprint .
```

Scan one manifest directly:

```bash
manifest-footprint ./requirements.txt
manifest-footprint ./package.json
```

Save a Markdown report:

```bash
manifest-footprint . --format markdown --output dependency-report.md
```

Save machine-readable JSON:

```bash
manifest-footprint . --format json --output dependency-report.json
```

If the command is not installed yet, it can also be run with:

```bash
python -m manifest_footprint . --format markdown
```

## How the status labels work

| Status | Meaning |
| --- | --- |
| `outdated` | A simple exact version pin is older than the latest stable release reported by the registry. |
| `current` | A simple exact version pin is not older than the latest stable release reported by the registry. |
| `review` | A version range or declaration was found, but this MVP cannot safely decide whether it needs an update. |
| `error` | The registry could not be reached or did not return usable metadata. |

Python exact pins such as `requests==2.31.0` can be compared using PEP 440 version rules. JavaScript exact `x.y.z` pins can be compared by their numeric components. npm ranges such as `^18.2.0` and Python ranges such as `>=2.0` are deliberately marked for review. A manifest declaration is not always the same as the version installed in an environment; lockfiles are needed for a more complete picture.

## Current limitations

- Only top-level `requirements.txt` and `package.json` files are discovered automatically.
- Nested requirements files and editable/VCS requirements are skipped with a warning.
- `pyproject.toml`, Poetry, Pipenv, pnpm, Yarn, and lockfiles are not supported yet.
- The tool checks direct dependencies only, not transitive dependencies.
- It does not currently check CVEs, license compatibility, package ownership, maintainer activity, or OpenSSF scores.
- Registry metadata can change, and the tool does not cache responses yet.

These limits are intentional for the first version. They are listed here so users know what the report does and does not tell them.

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Please open an issue before starting a large feature. Small bug reports, test cases, and documentation improvements are welcome.

## Roadmap

- [ ] Add lockfile support so the tool can compare resolved versions.
- [ ] Add `pyproject.toml` support.
- [ ] Add registry caching and clearer rate-limit handling.
- [ ] Add an optional GitHub Actions workflow example for users' own repositories.
- [ ] Research a reliable source for package maintenance and security signals.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the current contribution process.

## License

MIT. See [LICENSE](LICENSE).
