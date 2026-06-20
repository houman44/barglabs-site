#!/usr/bin/env python3
from __future__ import annotations

import sys
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for candidate in (
    os.environ.get("AELFRIC_ENGINE_PATH"),
    root,
    root / "aelfric-engine",
    root.parent / "aelfric-engine",
    root.parent / "alfred",
):
    if not candidate:
        continue
    engine_root = Path(candidate)
    if (engine_root / "aelfric_site_sync" / "__main__.py").exists():
        sys.path.insert(0, str(engine_root))
        break

from aelfric_site_sync.__main__ import main


if __name__ == "__main__":
    raise SystemExit(main(["--target", "barglabs", *sys.argv[1:]]))
