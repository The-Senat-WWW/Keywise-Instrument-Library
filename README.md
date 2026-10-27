# Keywise Instrument Library

A public catalog of SFZ instruments for Keywise Desktop.

## Status

The catalog structure is initialized, but **no instrument packages are published yet**. Instruments will be listed only after their source, redistribution permissions, package layout, and SHA-256 integrity have been verified.

## Principles

- **License first:** verify redistribution rights for the SFZ definition and all referenced samples.
- **Integrity:** calculate SHA-256 from the exact published archive and verify it before extraction.
- **Versioning:** publish versioned catalog metadata and immutable instrument packages.
- **Safe extraction:** reject absolute archive paths and parent-directory traversal.
- **Traceability:** record source, version, license, attribution, package size, and tested layout.
- **Independent library:** the catalog is not tied to any single soundbank.

## Repository layout

- `catalog/manifest.json` — machine-readable instrument catalog
- `schemas/instrument.schema.json` — manifest schema
- `docs/adding-instruments.md` — contribution and verification rules

## Add an instrument

See [Adding instruments](docs/adding-instruments.md) before proposing any package.

Public availability does not by itself grant permission to redistribute a file. No third-party instrument or sample will be added until its license terms have been checked.
