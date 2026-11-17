# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Verify listed code/data files against their recorded SHA-256 checksums."""
import argparse
import hashlib
import json
import os
from pathlib import Path

# Repository and interpreter artifacts are not distributed analysis inputs.
_IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__", "outputs"}


def distribution_files(root):
    for directory, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name not in _IGNORED_DIRECTORIES]
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            if relative == ".git" or name.endswith(".pyc"):
                continue
            yield relative


def verify(root):
    root = root.resolve()
    metadata = json.loads((root / "manifest.json").read_text(encoding="utf-8-sig"))
    errors = []
    seen = set()
    for item in metadata["files"]:
        name = item["path"]
        if name in seen:
            errors.append("duplicate:" + name)
        seen.add(name)
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            errors.append("unsafe path:" + name)
            continue
        if not path.is_file():
            errors.append("missing:" + name)
            continue
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1048576), b""):
                h.update(block)
        if h.hexdigest() != item["sha256"]:
            errors.append("hash mismatch:" + name)
        if path.stat().st_size != item["bytes"]:
            errors.append("size mismatch:" + name)
    extras = sorted(set(distribution_files(root)) - seen - {"manifest.json"})
    return {
        "package": root.name, "files_checked": len(seen),
        "passed": not errors and not extras, "errors": errors,
        "unlisted_files": extras,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, help="Code repository or extracted code directory")
    parser.add_argument("--data", type=Path, help="Extracted dataset directory")
    args = parser.parse_args()
    roots = [path for path in (args.code, args.data) if path is not None]
    if not roots:
        parser.error("Provide --code and/or --data")
    results = [verify(path) for path in roots]
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(result["passed"] for result in results) else 2)
