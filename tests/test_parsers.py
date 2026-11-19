import json

from manifest_footprint.parsers import parse_package_json, parse_requirements_file


def test_parse_requirements_file_skips_comments_and_options(tmp_path):
    manifest = tmp_path / "requirements.txt"
    manifest.write_text(
        "# comment\nrequests==2.31.0\nflask>=2.0\n-r other.txt\n-e git+https://example.com/pkg.git\n",
        encoding="utf-8",
    )

    result = parse_requirements_file(manifest)

    assert [item.name for item in result.dependencies] == ["requests", "flask"]
    assert result.dependencies[0].declared == "==2.31.0"
    assert len(result.warnings) == 2


def test_parse_package_json_reads_all_dependency_groups(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(
        json.dumps(
            {
                "dependencies": {"react": "^18.2.0"},
                "devDependencies": {"vitest": "1.0.0"},
                "optionalDependencies": {"fsevents": "~2.3.0"},
            }
        ),
        encoding="utf-8",
    )

    result = parse_package_json(manifest)

    assert {item.name for item in result.dependencies} == {"react", "vitest", "fsevents"}
    assert len(result.dependencies) == 3
