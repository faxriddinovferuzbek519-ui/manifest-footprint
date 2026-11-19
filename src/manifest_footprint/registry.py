"""Small read-only clients for the public PyPI and npm registries."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class RegistryError(RuntimeError):
    """Raised when a package's registry metadata cannot be retrieved."""


def fetch_json(url: str, timeout: float = 8.0) -> dict:
    """Fetch a JSON object from a public registry."""

    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "manifest-footprint/0.1.0",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryError(str(exc)) from exc
    if not isinstance(data, dict):
        raise RegistryError("registry returned an unexpected JSON response")
    return data


def latest_version(ecosystem: str, package_name: str, timeout: float = 8.0) -> tuple[str, str]:
    """Return (latest_version, registry_url) for a package."""

    if ecosystem == "pypi":
        encoded_name = quote(package_name, safe="")
        url = f"https://pypi.org/pypi/{encoded_name}/json"
        data = fetch_json(url, timeout=timeout)
        version = data.get("info", {}).get("version")
    elif ecosystem == "npm":
        encoded_name = quote(package_name, safe="@")
        url = f"https://registry.npmjs.org/{encoded_name}"
        data = fetch_json(url, timeout=timeout)
        version = data.get("dist-tags", {}).get("latest")
    else:
        raise RegistryError(f"unsupported package ecosystem: {ecosystem}")

    if not isinstance(version, str) or not version:
        raise RegistryError("registry response did not include a latest version")
    return version, url
