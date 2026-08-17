#!/usr/bin/env python3
import json
import sys
import zipfile
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def resolve_repo_file(repo_root: Path, relative: str | Path) -> Path:
    relative_path = Path(relative)
    current = repo_root

    for part in relative_path.parts:
        current = current / part

        if current.is_symlink():
            raise ValueError(f"symlink is not allowed: {relative}")

    path = (repo_root / relative_path).resolve(strict=True)

    if repo_root.resolve() not in path.parents:
        raise ValueError(f"path escapes repository root: {relative}")

    if not path.is_file():
        raise ValueError(f"missing file: {relative}")

    return path


def resolve_files(repo_root: Path, manifest: dict) -> list[Path]:
    files = [resolve_repo_file(repo_root, "manifest.json")]

    for script in manifest.get("content_scripts", []):
        for relative in script.get("js", []):
            files.append(resolve_repo_file(repo_root, relative))

    locale_root = repo_root / "_locales"

    if locale_root.is_symlink():
        raise ValueError("symlink is not allowed: _locales")

    if locale_root.exists():
        if not locale_root.is_dir():
            raise ValueError("_locales must be a directory")

        locale_dirs = sorted(locale_root.iterdir(), key=lambda path: path.name)

        for locale_dir in locale_dirs:
            if locale_dir.is_symlink():
                raise ValueError(f"symlink is not allowed: {locale_dir.relative_to(repo_root)}")

            if not locale_dir.is_dir():
                raise ValueError(f"locale entry must be a directory: {locale_dir.relative_to(repo_root)}")

            messages_path = locale_dir / "messages.json"
            relative_messages_path = messages_path.relative_to(repo_root)
            files.append(resolve_repo_file(repo_root, relative_messages_path))

        default_locale = manifest.get("default_locale")
        if default_locale:
            default_messages = locale_root / default_locale / "messages.json"

            if not default_messages.is_file():
                raise ValueError(f"missing default locale messages: {default_messages.relative_to(repo_root)}")

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
