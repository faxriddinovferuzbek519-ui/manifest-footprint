from manifest_footprint.parsers import Dependency
from manifest_footprint.scanner import check_dependency, classify


def test_python_exact_pin_is_outdated_when_registry_version_is_newer():
    dependency = Dependency("pypi", "requests", "==2.0.0", "requirements.txt")
    assert classify(dependency, "2.31.0")[0] == "outdated"


def test_python_range_is_reported_for_review_not_guessed():
    dependency = Dependency("pypi", "requests", ">=2.0", "requirements.txt")
    status, detail = classify(dependency, "2.31.0")
    assert status == "review"
    assert "lockfile" in detail


def test_npm_range_is_not_mislabelled_as_outdated():
    dependency = Dependency("npm", "react", "^18.2.0", "package.json")
    assert classify(dependency, "19.0.0")[0] == "review"


def test_registry_error_is_kept_in_report():
    dependency = Dependency("pypi", "unknown-package", "(not specified)", "requirements.txt")

    def fail_lookup(_ecosystem, _name, _timeout):
        raise OSError("network unavailable")

    finding = check_dependency(dependency, version_lookup=fail_lookup)
    assert finding.status == "error"
    assert "network unavailable" in finding.detail


def test_exact_npm_version_can_be_compared():
    dependency = Dependency("npm", "react", "18.2.0", "package.json")
    assert classify(dependency, "18.3.0")[0] == "outdated"
