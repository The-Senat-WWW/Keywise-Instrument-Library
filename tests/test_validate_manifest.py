import unittest

from scripts.validate_manifest import validate


def valid_instrument(instrument_id="test-piano"):
    return {
        "id": instrument_id,
        "name": "Test Piano",
        "version": "1.0",
        "description": "A fixture instrument",
        "license": {
            "spdx_id": "CC0-1.0",
            "redistribution_verified": True,
            "attribution": "No attribution required",
            "url": "https://creativecommons.org/publicdomain/zero/1.0/",
        },
        "source": {"url": "https://example.org/source", "revision": "v1"},
        "package": {
            "url": "https://example.org/test-piano.zip",
            "sha256": "a" * 64,
            "format": "zip",
            "size_bytes": 1234,
        },
        "sfz_files": ["Test Piano.sfz"],
        "tags": ["piano"],
    }


def valid_manifest(instruments=None):
    return {
        "schema_version": 1,
        "catalog_version": "0.1.0",
        "generated_at": None,
        "instruments": [] if instruments is None else instruments,
    }


class ValidateManifestTests(unittest.TestCase):
    def test_empty_catalog_is_valid(self):
        self.assertEqual(validate(valid_manifest()), [])

    def test_valid_instrument_is_accepted(self):
        self.assertEqual(validate(valid_manifest([valid_instrument()])), [])

    def test_duplicate_ids_are_rejected(self):
        errors = validate(valid_manifest([valid_instrument(), valid_instrument()]))
        self.assertTrue(any("duplicate instrument id" in error for error in errors))

    def test_bad_checksum_is_rejected(self):
        instrument = valid_instrument()
        instrument["package"]["sha256"] = "not-a-hash"
        errors = validate(valid_manifest([instrument]))
        self.assertTrue(any("sha256" in error for error in errors))

    def test_unverified_redistribution_is_rejected(self):
        instrument = valid_instrument()
        instrument["license"]["redistribution_verified"] = False
        errors = validate(valid_manifest([instrument]))
        self.assertTrue(any("redistribution_verified" in error for error in errors))

    def test_unsafe_or_non_http_package_url_is_rejected(self):
        instrument = valid_instrument()
        instrument["package"]["url"] = "file:///tmp/archive.zip"
        errors = validate(valid_manifest([instrument]))
        self.assertTrue(any("package.url" in error for error in errors))

    def test_bad_instrument_id_is_rejected(self):
        errors = validate(valid_manifest([valid_instrument("Test Piano")]))
        self.assertTrue(any("kebab-case" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
