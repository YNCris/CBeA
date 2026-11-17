# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Validate release content hashes without importing scientific dependencies."""
import argparse,hashlib,json
from pathlib import Path
def verify(root):
    root=root.resolve()
    metadata=json.loads((root/"manifest.json").read_text(encoding="utf-8-sig"))
    errors=[]
    seen=set()
    for item in metadata["files"]:
        name=item["path"]
        if name in seen:errors.append("duplicate:"+name)
        seen.add(name)
        path=(root/name).resolve()
        if not path.is_relative_to(root):
            errors.append("unsafe path:"+name);continue
        if not path.is_file():
            errors.append("missing:"+name);continue
        h=hashlib.sha256()
        with path.open("rb") as f:
            for b in iter(lambda:f.read(1048576),b""):h.update(b)
        if h.hexdigest()!=item["sha256"]:errors.append("hash mismatch:"+name)
        if path.stat().st_size!=item["bytes"]:errors.append("size mismatch:"+name)
    actual={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    extras=sorted(actual-seen-{"manifest.json"})
    return {"package":root.name,"files_checked":len(seen),"passed":not errors and not extras,"errors":errors,"unlisted_files":extras}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--code",type=Path)
    ap.add_argument("--data",type=Path)
    args=ap.parse_args()
    roots=[p for p in (args.code,args.data) if p is not None]
    if not roots:ap.error("Provide --code and/or --data")
    results=[verify(p) for p in roots]
    print(json.dumps(results,indent=2))
    raise SystemExit(0 if all(r["passed"] for r in results) else 2)
