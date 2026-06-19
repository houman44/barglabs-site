from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .engine import run_target_audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Aelfric propose-only public-site sync audit. Opens proposals; never edits, commits, deploys, or publishes.",
    )
    parser.add_argument("--target", required=True, choices=("egbert", "barglabs"))
    parser.add_argument("--root", "--site-root", dest="root", type=Path, default=Path.cwd())
    parser.add_argument("--product-root", action="append", type=Path, default=[])
    parser.add_argument("--products", default="alfred,egbert,edwin,therasyn,sara,knut,henry,edwy,simba,wilfrid")
    parser.add_argument("--portfolio-feed", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--github-output")
    parser.add_argument("--no-live", action="store_true")
    parser.add_argument("--exit-code-on-drift", action="store_true")
    args = parser.parse_args(argv)

    env_roots = [Path(part) for part in os.environ.get("PRODUCT_STATUS_ROOTS", "").split(os.pathsep) if part]
    products = tuple(part.strip() for part in args.products.split(",") if part.strip())
    report = run_target_audit(
        args.target,
        args.root,
        fetch_live=not args.no_live,
        product_roots=tuple(args.product_root + env_roots),
        portfolio_feed=args.portfolio_feed,
        products=products,
    )
    markdown = report.to_markdown()
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)
    if args.json_output:
        args.json_output.write_text(
            json.dumps([finding.to_dict() for finding in report.findings], indent=2) + "\n",
            encoding="utf-8",
        )
    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"drift_found={'true' if report.findings else 'false'}\n")
            handle.write(f"has_drift={'true' if report.findings else 'false'}\n")
            handle.write(f"finding_count={len(report.findings)}\n")
    return 1 if args.exit_code_on_drift and report.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
