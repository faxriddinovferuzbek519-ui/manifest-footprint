# Contributing

Thanks for considering a contribution to Manifest Footprint. The project is new, so feedback and small improvements are especially useful.

## Before opening a pull request

1. Check the existing issues to see whether the problem has already been reported.
2. For a larger change, open an issue first so we can agree on the approach.
3. Keep changes focused and add tests for bug fixes or new behavior.
4. Update the README when a change affects supported inputs or output.

## Set up locally

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

## Pull requests

Please describe the problem, the change, and how you tested it. Do not include real access tokens, private project files, or other secrets in examples or test fixtures.

## Scope

The project aims to give developers understandable dependency information. Reports should distinguish verified facts from signals that need a human review. Please avoid adding a status that sounds certain when the underlying data cannot support that conclusion.
