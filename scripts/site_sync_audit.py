#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import html.parser
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


SITE_TEXT_GLOBS = ("app/**/*.tsx", "app/**/*.ts", "app/**/*.mdx", "components/**/*.tsx", "components/**/*.ts")
DEFAULT_PRODUCTS = ("alfred", "egbert", "edwin", "therasyn", "sara", "knut", "henry", "edwy", "simba", "wilfrid")
PRODUCT_ALIASES = {"sara": ("sara", "site-machine", "site_machine")}
WALL_LIST_PATTERNS = (
    re.compile(r"\breturns\b", re.IGNORECASE),
    re.compile(r"\bNAV\b"),
    re.compile(r"\bnet asset value\b", re.IGNORECASE),
    re.compile(r"\bAUM\b"),
    re.compile(r"\bassets under management\b", re.IGNORECASE),
    re.compile(r"\bcustomers?\b", re.IGNORECASE),
    re.compile(r"\btraction\b", re.IGNORECASE),
    re.compile(r"\bSOC\s?2\b", re.IGNORECASE),
)
ROSTER_STALE_NAMES = {
    "Niels": "Niels has been removed from Barg Labs. Remove or replace this with current human-approved roster language.",
    "Amirali": "Amirali is a Wilfrid customer-zero student, not a Barg Labs team/cap-table member. Do not present him as team.",
}
THESIS_OVERCLAIM_PATTERNS = (
    "all ten products are live",
    "shared substrate for all ten products",
    "every product runs on alfred",
    "fully live substrate",
)
PRODUCT_EXPECTATIONS = {
    "Alfred": {
        "allowed_status_terms": ("console", "live", "operator surface", "mission-control", "operator os"),
        "overclaim_terms": ("all products live", "all ten products", "external customers"),
    },
    "Egbert": {
        "allowed_status_terms": ("paper", "paper-mode", "paper pilot", "pilot"),
        "overclaim_terms": ("production", "live trading", "returns", "nav", "aum", "customer traction"),
    },
    "Edwin": {
        "allowed_status_terms": ("personal", "trading", "fx", "houman", "go-live gates"),
        "overclaim_terms": ("b2b", "customer traction", "public fund", "aum"),
    },
    "Therasyn": {
        "allowed_status_terms": ("parked", "pending md", "md co-founder", "clinical"),
        "overclaim_terms": ("live", "customer", "production", "baa-bound", "on-prem capable from day one", "health systems can run"),
    },
    "Sara": {
        "allowed_status_terms": ("site-machine", "mvp", "pilot", "landing-page", "website generation"),
        "overclaim_terms": ("fully shipped", "production customers", "traction"),
    },
    "Knut": {
        "allowed_status_terms": ("observation", "advisor", "mvp", "pilot"),
        "overclaim_terms": ("registered cta", "live advisory customers", "aum"),
    },
    "Henry": {
        "allowed_status_terms": ("pre-mvp", "planned", "scaffold", "accounting"),
        "overclaim_terms": ("live", "customers", "production"),
    },
    "Edwy": {
        "allowed_status_terms": ("public", "portal", "literacy", "primer", "launch"),
        "overclaim_terms": ("paid customers", "traction", "enterprise"),
    },
    "Simba": {
        "allowed_status_terms": ("pre-mvp", "internal", "scaffold", "simulation"),
        "overclaim_terms": ("live", "customers", "production"),
    },
    "Wilfrid": {
        "allowed_status_terms": ("private", "tutor", "customer-zero", "phase 1"),
        "overclaim_terms": ("public launch", "customers", "production"),
    },
}


@dataclasses.dataclass(frozen=True)
class AuditConfig:
    site_root: Path
    product_roots: tuple[Path, ...] = ()
    live_url: str = "https://barglabs.ai"
    check_live: bool = True
    products: tuple[str, ...] = DEFAULT_PRODUCTS
    alfred_portfolio_feed: str | None = None


@dataclasses.dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    location: str
    current_copy: str
    proposed_copy: str
    evidence: str
    product: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return dataclasses.asdict(self)


class TextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.parts.append(value)


def collect_findings(config: AuditConfig) -> list[Finding]:
    site_documents = read_site_documents(config.site_root)
    if config.check_live:
        site_documents.extend(fetch_live_document(config.live_url))

    statuses = read_product_statuses(config.product_roots)
    findings: list[Finding] = []
    findings.extend(check_wall_list(site_documents))
    findings.extend(check_roster(site_documents))
    findings.extend(check_product_status(site_documents, statuses, config.products))
    findings.extend(check_links(site_documents))
    findings.extend(check_thesis(site_documents))
    findings.extend(check_brand_voice(site_documents))

    if config.alfred_portfolio_feed:
        findings.extend(check_portfolio_feed_placeholder(config.alfred_portfolio_feed))

    return sorted(findings, key=lambda item: (severity_rank(item.severity), item.code, item.location))


def read_site_documents(site_root: Path) -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []
    for pattern in SITE_TEXT_GLOBS:
        for path in sorted(site_root.glob(pattern)):
            if path.is_file():
                documents.append((str(path.relative_to(site_root)), path.read_text(encoding="utf-8")))
    return documents


def fetch_live_document(live_url: str) -> list[tuple[str, str]]:
    request = urllib.request.Request(live_url, headers={"User-Agent": "barglabs-site-sync-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(1_000_000).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return [
            (
                live_url,
                f"LIVE_FETCH_FAILED: {type(exc).__name__}: {exc}",
            )
        ]
    parser = TextExtractor()
    parser.feed(raw)
    return [(live_url, "\n".join(parser.parts))]


def read_product_statuses(product_roots: Iterable[Path]) -> dict[str, tuple[Path, str]]:
    statuses: dict[str, tuple[Path, str]] = {}
    for root in product_roots:
        if not root.exists():
            continue
        for status_path in sorted(root.glob("*/STATUS.md")):
            product_key = normalize_product_name(status_path.parent.name)
            statuses.setdefault(product_key, (status_path, status_path.read_text(encoding="utf-8")))
    return statuses


def check_wall_list(documents: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for location, text in documents:
        for pattern in WALL_LIST_PATTERNS:
            for match in pattern.finditer(text):
                excerpt = excerpt_around(text, match.start(), match.end())
                if is_wall_list_context_allowed(excerpt):
                    continue
                findings.append(
                    Finding(
                        code="wall-list-term",
                        severity="high",
                        location=location,
                        current_copy=excerpt,
                        proposed_copy="Remove or replace wall-list language unless a human explicitly approves a cited compliance-safe source.",
                        evidence="Barg Labs wall-list: no returns, NAV, AUM, customer, traction, or SOC2 claims for any product.",
                    )
                )
    return dedupe_findings(findings)


def check_roster(documents: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for location, text in documents:
        for name, proposed in ROSTER_STALE_NAMES.items():
            pattern = re.compile(rf"\b{re.escape(name)}\b")
            for match in pattern.finditer(text):
                findings.append(
                    Finding(
                        code="roster-stale-name",
                        severity="high",
                        location=location,
                        current_copy=excerpt_around(text, match.start(), match.end()),
                        proposed_copy=proposed,
                        evidence="Team roster instruction: Houman founder/CTO; Nima and Pooneh co-founders; Carolynn GTM TBD; Niels removed; Amirali is customer-zero student.",
                    )
                )
    return dedupe_findings(findings)


def check_product_status(
    documents: list[tuple[str, str]], statuses: dict[str, tuple[Path, str]], products: Iterable[str]
) -> list[Finding]:
    findings: list[Finding] = []
    site_text = "\n".join(text for _, text in documents)
    products_present = products_mentioned(site_text, products)

    for product in products_present:
        status_key = normalize_product_name(product)
        status_entry = statuses.get(status_key)
        if status_entry is None:
            findings.append(
                Finding(
                    code="missing-product-evidence",
                    severity="medium",
                    location="product evidence",
                    product=product,
                    current_copy=f"{product} appears in site copy.",
                    proposed_copy=f"Flag {product} for human judgment until STATUS.md or Alfred operator-summary evidence is available.",
                    evidence=f"No reachable STATUS.md for {product} under configured product roots.",
                )
            )
            continue

        status_path, status_text = status_entry
        current_lines = lines_for_product(documents, product)
        evidence = summarize_status_evidence(status_path, status_text)
        found_drift_for_product = False
        for current in current_lines:
            overclaim = product_overclaim(product, current, status_text)
            if overclaim:
                findings.append(
                    Finding(
                        code="product-status-drift",
                        severity="high",
                        location=overclaim[0],
                        product=product,
                        current_copy=overclaim[1],
                        proposed_copy=proposed_status_copy(product, status_text),
                        evidence=evidence,
                    )
                )
                found_drift_for_product = True
            if found_drift_for_product:
                break
    return dedupe_findings(findings)


def check_links(documents: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    href_pattern = re.compile(r"href=[\"']([^\"']+)[\"']")
    expected_links = {
        "Egbert": "https://egbert.io",
        "Alfred": "https://alfred.barglabs.ai/mission-control",
        "Therasyn": "https://therasyn.ai",
        "Edwy": "https://edwy.barglabs.ai",
    }
    for location, text in documents:
        hrefs = href_pattern.findall(text)
        for href in hrefs:
            if href == "#":
                findings.append(
                    Finding(
                        code="dead-or-self-link",
                        severity="medium",
                        location=location,
                        current_copy='href="#"',
                        proposed_copy="Use a real section id, product URL, mailto link, or remove the link.",
                        evidence="Self-links are not useful CTAs for barglabs.ai sync.",
                    )
                )
            if href.startswith("http"):
                findings.extend(check_http_link(location, href))

        if "href=" not in text:
            continue
        for product, expected_href in expected_links.items():
            if product.lower() in text.lower() and expected_href not in text:
                findings.append(
                    Finding(
                        code="wrong-product-link",
                        severity="medium",
                        location=location,
                        product=product,
                        current_copy=f"{product} appears without expected link {expected_href}.",
                        proposed_copy=f"Point {product} CTA/card link to {expected_href} or flag why it is intentionally absent.",
                        evidence=f"Expected product URL mapping: {product} -> {expected_href}.",
                    )
                )
    return dedupe_findings(findings)


def check_http_link(location: str, href: str) -> list[Finding]:
    request = urllib.request.Request(href, headers={"User-Agent": "barglabs-site-sync-audit/1.0"}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return [
            Finding(
                code="dead-or-wrong-link",
                severity="medium",
                location=location,
                current_copy=href,
                proposed_copy="Verify or replace this product/CTA link before editing site copy.",
                evidence=f"Link check failed: {type(exc).__name__}: {exc}",
            )
        ]
    if status >= 400:
        return [
            Finding(
                code="dead-or-wrong-link",
                severity="medium",
                location=location,
                current_copy=href,
                proposed_copy="Replace or remove this product/CTA link.",
                evidence=f"HTTP HEAD returned {status}.",
            )
        ]
    return []


def check_thesis(documents: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    for location, text in documents:
        lowered = text.lower()
        for phrase in THESIS_OVERCLAIM_PATTERNS:
            index = lowered.find(phrase)
            if index == -1:
                continue
            findings.append(
                Finding(
                    code="substrate-thesis-overclaim",
                    severity="medium",
                    location=location,
                    current_copy=excerpt_around(text, index, index + len(phrase)),
                    proposed_copy="Lead with Alfred Console as live and describe the broader L4/L5 substrate as partly aspirational until Alfred operator-summary evidence proves otherwise.",
                    evidence="Alfred ADR/status alignment: shared substrate is emerging; most portfolio products are pre-MVP or gated.",
                )
            )
    return findings


def check_brand_voice(documents: list[tuple[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    emoji_pattern = re.compile("[\U0001F300-\U0001FAFF]")
    for location, text in documents:
        for match in emoji_pattern.finditer(text):
            findings.append(
                Finding(
                    code="brand-voice-emoji",
                    severity="medium",
                    location=location,
                    current_copy=excerpt_around(text, match.start(), match.end()),
                    proposed_copy="Remove emoji. Barg Labs product copy should stay calm and quiet.",
                    evidence="Brand voice constraint: no emojis.",
                )
            )
    return findings


def check_portfolio_feed_placeholder(feed: str) -> list[Finding]:
    if feed.startswith(("http://", "https://")):
        return []
    path = Path(feed)
    if path.exists():
        return []
    return [
        Finding(
            code="missing-portfolio-feed",
            severity="low",
            location="Alfred portfolio feed",
            current_copy=feed,
            proposed_copy="Continue reading per-product STATUS.md until Alfred operator-summary aggregation is wired.",
            evidence="Configured ALFRED_PORTFOLIO_FEED was not reachable.",
        )
    ]


def products_mentioned(site_text: str, products: Iterable[str]) -> list[str]:
    mentioned: list[str] = []
    for product in products:
        if re.search(rf"\b{re.escape(product)}\b", site_text, re.IGNORECASE):
            mentioned.append(canonical_product(product))
    return mentioned


def lines_for_product(documents: list[tuple[str, str]], product: str) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    pattern = re.compile(rf"\b{re.escape(product)}\b", re.IGNORECASE)
    for location, text in documents:
        split_lines = text.splitlines()
        for line_no, line in enumerate(split_lines, start=1):
            if not pattern.search(line):
                continue
            window_start = line_no - 1
            window_end = min(len(split_lines), line_no + 9)
            window = " ".join(part.strip() for part in split_lines[window_start:window_end])
            lines.append((f"{location}:{line_no}", " ".join(window.split())[:900]))
    return lines


def product_overclaim(product: str, current: tuple[str, str], status_text: str) -> tuple[str, str] | None:
    location, copy = current
    expectation = PRODUCT_EXPECTATIONS.get(product, {})
    copy_lower = copy.lower()
    status_lower = status_text.lower()
    overclaim_terms = expectation.get("overclaim_terms", ())
    if not any(term in copy_lower for term in overclaim_terms):
        return None
    allowed_terms = expectation.get("allowed_status_terms", ())
    if allowed_terms and any(term in status_lower for term in allowed_terms):
        return (location, copy)
    return (location, copy)


def proposed_status_copy(product: str, status_text: str) -> str:
    status_lower = status_text.lower()
    if product == "Egbert" and "paper" in status_lower:
        return "Describe Egbert as governed paper-pilot infrastructure; do not imply production/live trading, returns, NAV, AUM, or customer traction."
    if product == "Alfred" and ("console" in status_lower or "mission" in status_lower):
        return "Describe Alfred as Console/operator surface live, without implying all portfolio products run on a completed substrate."
    if product == "Sara" and ("mvp" in status_lower or "pilot" in status_lower):
        return "Describe Sara/Site Machine as MVP/pilot-gated landing-page generation, not broad customer traction."
    return f"Align {product} wording to cited STATUS evidence; flag uncertain positioning for human review."


def summarize_status_evidence(status_path: Path, status_text: str) -> str:
    preferred_markers = (
        "one-line state",
        "phase",
        "paper",
        "pilot",
        "mvp",
        "parked",
        "no paying",
        "no signed",
        "no live deployment",
        "blocked",
    )
    for line in status_text.splitlines():
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("|")
            and not stripped.startswith("#")
            and len(stripped) < 260
            and any(marker in stripped.lower() for marker in preferred_markers)
        ):
            return f"{status_path}: {stripped}"
    for line in status_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("|") and len(stripped) < 260:
            return f"{status_path}: {stripped}"
    return f"{status_path}: STATUS.md present."


def is_wall_list_context_allowed(excerpt: str) -> bool:
    lowered = excerpt.lower()
    allowed_markers = ("no return", "no returns", "wall-list", "do not", "never", "remove")
    return any(marker in lowered for marker in allowed_markers)


def excerpt_around(text: str, start: int, end: int, radius: int = 110) -> str:
    prefix = max(0, start - radius)
    suffix = min(len(text), end + radius)
    excerpt = " ".join(text[prefix:suffix].split())
    return excerpt[:260]


def normalize_product_name(name: str) -> str:
    normalized = name.strip().lower().replace("_", "-")
    for canonical, aliases in PRODUCT_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def canonical_product(name: str) -> str:
    key = normalize_product_name(name)
    return {
        "alfred": "Alfred",
        "egbert": "Egbert",
        "edwin": "Edwin",
        "therasyn": "Therasyn",
        "sara": "Sara",
        "knut": "Knut",
        "henry": "Henry",
        "edwy": "Edwy",
        "simba": "Simba",
        "wilfrid": "Wilfrid",
    }.get(key, name)


def dedupe_findings(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str, str | None]] = set()
    deduped: list[Finding] = []
    for finding in findings:
        key = (finding.code, finding.location, finding.current_copy, finding.product)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def severity_rank(severity: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(severity, 3)


def render_report(findings: list[Finding], generated_at: dt.datetime | None = None) -> str:
    generated = generated_at or dt.datetime.now(dt.UTC)
    lines = [
        "# barglabs.ai Sync Proposal",
        "",
        f"Generated: {generated.isoformat(timespec='seconds')}",
        "",
        "This is a proposal-only audit. It does not edit site copy, commit, merge, deploy, or publish.",
        "",
    ]
    if not findings:
        lines.extend(["## Findings", "", "No drift found by the deterministic audit."])
        return "\n".join(lines) + "\n"

    lines.extend(["## Findings", ""])
    for index, finding in enumerate(findings, start=1):
        product = f" ({finding.product})" if finding.product else ""
        lines.extend(
            [
                f"### {index}. {finding.code}{product}",
                "",
                f"- Severity: {finding.severity}",
                f"- Location: `{finding.location}`",
                f"- Current copy: {finding.current_copy}",
                f"- Proposed copy: {finding.proposed_copy}",
                f"- Evidence: {finding.evidence}",
                "",
            ]
        )
    return "\n".join(lines)


def config_from_args(argv: list[str]) -> tuple[AuditConfig, Path | None, Path | None]:
    parser = argparse.ArgumentParser(description="Audit barglabs.ai copy against portfolio source-of-truth.")
    parser.add_argument("--site-root", type=Path, default=Path.cwd())
    parser.add_argument("--product-root", action="append", type=Path, default=[])
    parser.add_argument("--products", default=",".join(DEFAULT_PRODUCTS))
    parser.add_argument("--live-url", default="https://barglabs.ai")
    parser.add_argument("--check-live", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)

    env_roots = [Path(part) for part in os.environ.get("PRODUCT_STATUS_ROOTS", "").split(os.pathsep) if part]
    product_roots = tuple(args.product_root + env_roots)
    products = tuple(part.strip() for part in args.products.split(",") if part.strip())
    config = AuditConfig(
        site_root=args.site_root,
        product_roots=product_roots,
        live_url=args.live_url,
        check_live=args.check_live,
        products=products,
        alfred_portfolio_feed=os.environ.get("ALFRED_PORTFOLIO_FEED"),
    )
    return config, args.output, args.json_output


def main(argv: list[str]) -> int:
    config, output_path, json_output_path = config_from_args(argv)
    findings = collect_findings(config)
    report = render_report(findings)
    if output_path:
        output_path.write_text(report, encoding="utf-8")
    else:
        print(report)
    if json_output_path:
        json_output_path.write_text(
            json.dumps([finding.to_dict() for finding in findings], indent=2) + "\n",
            encoding="utf-8",
        )
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
