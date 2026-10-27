#!/usr/bin/env python3
"""Validate the published Keywise instrument catalog using only the Python stdlib."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "catalog" / "manifest.json"
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
INSTRUMENT_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
FORMATS = {"zip", "tar", "tar.gz", "tar.bz2", "tar.xz"}


def is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest must be a JSON object"]

    for field in ("schema_version", "catalog_version", "instruments"):
        if field not in data:
            errors.append(f"missing required top-level field: {field}")
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(data.get("catalog_version"), str) or not SEMVER.fullmatch(data["catalog_version"]):
        errors.append("catalog_version must use MAJOR.MINOR.PATCH numeric format")
    if "generated_at" in data and data["generated_at"] is not None:
        if not isinstance(data["generated_at"], str) or not data["generated_at"].endswith("Z"):
            errors.append("generated_at must be null or an ISO-8601 UTC timestamp ending in Z")

    instruments = data.get("instruments")
    if not isinstance(instruments, list):
        errors.append("instruments must be an array")
        return errors

    seen_ids: set[str] = set()
    for index, item in enumerate(instruments):
        prefix = f"instruments[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue

        for field in ("id", "name", "version", "description", "license", "source", "package"):
            if field not in item:
                errors.append(f"{prefix} missing required field: {field}")

        instrument_id = item.get("id")
        if not isinstance(instrument_id, str) or not INSTRUMENT_ID.fullmatch(instrument_id):
            errors.append(f"{prefix}.id must be lowercase kebab-case")
        elif instrument_id in seen_ids:
            errors.append(f"duplicate instrument id: {instrument_id}")
        else:
            seen_ids.add(instrument_id)

        for field in ("name", "version"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if not isinstance(item.get("description"), str):
            errors.append(f"{prefix}.description must be a string")

        license_data = item.get("license")
        if not isinstance(license_data, dict):
            errors.append(f"{prefix}.license must be an object")
        else:
            for field in ("spdx_id", "redistribution_verified", "attribution"):
                if field not in license_data:
                    errors.append(f"{prefix}.license missing required field: {field}")
            if license_data.get("redistribution_verified") is not True:
                errors.append(f"{prefix}.license.redistribution_verified must be true before publication")
            if license_data.get("spdx_id") is not None and not isinstance(license_data.get("spdx_id"), str):
                errors.append(f"{prefix}.license.spdx_id must be a string or null")
            if not isinstance(license_data.get("attribution"), str):
                errors.append(f"{prefix}.license.attribution must be a string")
            if license_data.get("url") is not None and not is_http_url(license_data["url"]):
                errors.append(f"{prefix}.license.url must be an HTTP(S) URL or null")

        source = item.get("source")
        if not isinstance(source, dict) or not is_http_url(source.get("url")):
            errors.append(f"{prefix}.source.url must be an HTTP(S) URL")

        package = item.get("package")
        if not isinstance(package, dict):
            errors.append(f"{prefix}.package must be an object")
            continue
        if not is_http_url(package.get("url")):
            errors.append(f"{prefix}.package.url must be an HTTP(S) URL")
        if not isinstance(package.get("sha256"), str) or not SHA256.fullmatch(package["sha256"]):
            errors.append(f"{prefix}.package.sha256 must contain exactly 64 hexadecimal characters")
        if package.get("format") not in FORMATS:
            errors.append(f"{prefix}.package.format must be one of: {', '.join(sorted(FORMATS))}")
        size = package.get("size_bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 1:
            errors.append(f"{prefix}.package.size_bytes must be a positive integer")

        if "sfz_files" in item:
            sfz_files = item["sfz_files"]
            if not isinstance(sfz_files, list) or not sfz_files or any(not isinstance(p, str) or not p.strip() for p in sfz_files):
                errors.append(f"{prefix}.sfz_files must be a non-empty array of non-empty strings")
        if "tags" in item and (not isinstance(item["tags"], list) or any(not isinstance(tag, str) for tag in item["tags"])):
            errors.append(f"{prefix}.tags must be an array of strings")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MANIFEST
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON from {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {path} is valid ({len(data['instruments'])} instruments)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
