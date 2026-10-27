# Adding instruments

Do not add an instrument until its source and redistribution rights have been checked.

## Required checks

1. **Identify the source.** Record the canonical project or creator URL and exact source version/revision.
2. **Verify redistribution rights.** Public availability does not grant redistribution permission. Check the license for the SFZ definition and every referenced sample; record attribution and notices.
3. **Prepare a reproducible package.** Include all required samples in a documented layout. Avoid absolute sample paths and references outside the instrument directory.
4. **Publish an immutable package.** Prefer a versioned release asset or another stable HTTPS URL. Do not point a released catalog at a mutable archive.
5. **Calculate SHA-256 from the final archive bytes.** Never guess or publish an unverified digest.
6. **Validate the archive layout.** Check the expected directory, file sizes, SFZ references, and archive paths. Reject absolute paths and parent-directory traversal.
7. **Test installation.** Confirm that hash mismatches are rejected before extraction and all sample references resolve after installation.
8. **Update the manifest.** Add complete metadata and increment the catalog version.

## Manifest requirements

Each instrument needs a unique stable ID, instrument version, source URL, package URL, exact SHA-256 digest, archive format and size, and license/attribution metadata. Set `redistribution_verified` to `true` only after the actual terms have been checked.

## Do not

- Upload third-party samples without permission to redistribute them.
- Treat HTTPS or a reputable host as proof that an archive is authentic.
- Invent checksums.
- Extract an archive before verifying its checksum.
- Trust archive paths without validating them.
- Silently substitute a different instrument when one is unavailable.


## Run catalog checks locally

From the repository root, run:

```sh
python scripts/validate_manifest.py
python -m unittest discover -s tests -v
```

The validator checks required metadata, unique IDs, HTTP(S) source/package URLs, SHA-256 syntax, archive format, positive package size, and explicit confirmation that redistribution rights were verified. It does **not** independently download packages, calculate their hashes, or determine whether a license interpretation is legally correct; those remain release-review steps. GitHub Actions runs these checks on pushes and pull requests targeting `main`.
