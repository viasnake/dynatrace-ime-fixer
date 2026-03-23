#!/usr/bin/env python3
import json
import sys
import zipfile
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def resolve_files(repo_root: Path, manifest: dict) -> list[Path]:
    files = [repo_root / "manifest.json"]

    for script in manifest.get("content_scripts", []):
        for relative in script.get("js", []):
            relative_path = Path(relative)
            path = repo_root / relative_path
            current = repo_root

            for part in relative_path.parts:
                current = current / part

                if current.is_symlink():
                    raise ValueError(f"symlink is not allowed: {relative}")

            path = path.resolve(strict=True)

            if repo_root.resolve() not in path.parents:
                raise ValueError(f"path escapes repository root: {relative}")

            if not path.is_file():
                raise ValueError(f"missing content script file: {relative}")

            files.append(path)

    unique_files = []
    seen = set()

    for file_path in files:
        normalized = file_path.resolve()

        if normalized in seen:
            continue

        seen.add(normalized)
        unique_files.append(normalized)

    return unique_files


def write_zip(repo_root: Path, archive_path: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(repo_root).as_posix())


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: build_zip.py <repo_root> <archive_path>", file=sys.stderr)
        return 1

    repo_root = Path(sys.argv[1]).resolve()
    archive_path = Path(sys.argv[2]).resolve()
    dist_dir = (repo_root / "dist").resolve()
    manifest_path = repo_root / "manifest.json"

    if dist_dir not in archive_path.parents:
        print(f"archive path must be under dist/: {archive_path}", file=sys.stderr)
        return 1

    if not manifest_path.exists():
        print(f"manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_manifest(manifest_path)
    files = resolve_files(repo_root, manifest)
    write_zip(repo_root, archive_path, files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
