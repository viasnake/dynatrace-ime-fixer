#!/usr/bin/env python3
import re
import sys
from pathlib import Path

from build_zip import load_manifest, resolve_files, write_zip

SUPPORTED_TARGETS = ("chrome", "firefox")
VERSION_PATTERN = re.compile(r"^[0-9A-Za-z._-]+$")


def parse_targets(argv: list[str]) -> list[str]:
    if len(argv) <= 1:
        return list(SUPPORTED_TARGETS)

    target = argv[1]
    if target not in SUPPORTED_TARGETS:
        print("Usage: package_extension.py [chrome|firefox]", file=sys.stderr)
        raise SystemExit(1)

    return [target]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "manifest.json"
    dist_dir = repo_root / "dist"
    targets = parse_targets(sys.argv)

    manifest = load_manifest(manifest_path)
    version = manifest.get("version", "")

    if not VERSION_PATTERN.match(version):
        print(f"Unsupported manifest version for packaging: {version}", file=sys.stderr)
        return 1

    files = resolve_files(repo_root, manifest)
    dist_dir.mkdir(parents=True, exist_ok=True)

    for target in targets:
        archive_path = dist_dir / f"dynatrace-ime-fixer-{target}-{version}.zip"

        if archive_path.exists():
            archive_path.unlink()

        write_zip(repo_root, archive_path, files)
        print(f"Created {archive_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
