from __future__ import annotations

import dataclasses
import datetime as dt
import html.parser
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Sequence


EG_BERT_PUBLIC_FILES = {
    "About.tsx",
    "Contact.tsx",
    "ForBrokers.tsx",
    "ForPropHF.tsx",
    "ForRIA.tsx",
    "Glossary.tsx",
    "HowItWorks.tsx",
    "Landing.tsx",
    "Legal.tsx",
    "Pillars.tsx",
    "Pricing.tsx",
    "Products.tsx",
    "RiskDisclosure.tsx",
    "Trust.tsx",
    "marketingRoutes.json",
    "marketingMeta.ts",
}

DEFAULT_PRODUCTS = ("alfred", "egbert", "edwin", "therasyn", "sara", "knut", "henry", "edwy", "simba", "wilfrid")
PRODUCT_ALIASES = {"sara": ("sara", "site-machine", "site_machine")}


@dataclasses.dataclass(frozen=True)
class TextHit:
    path: str
    line_number: int
    line: str

    @property
    def location(self) -> str:
        return f"{self.path}:{self.line_number}"


@dataclasses.dataclass(frozen=True)
class SourceEvidence:
    product: str
    mode: str
    evidence: str
    status_text: str


@dataclasses.dataclass(frozen=True)
class LiveFetch:
    url: str
    ok: bool
    status: int | None
    summary: str


@dataclasses.dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    location: str
    current_copy: str
    proposed_copy: str
    evidence: str
    product: str | None = None
    drift_class: str = ""

    def to_dict(self) -> dict[str, str | None]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class AuditReport:
    target: str
    title: str
    generated_at: str
    findings: tuple[Finding, ...]
    sources: tuple[SourceEvidence, ...]
    live_fetches: tuple[LiveFetch, ...]
    source_mode: str

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            f"Generated: {self.generated_at}",
            "",
            "Mode: PROPOSE-ONLY. This report does not edit site copy, commit, merge, deploy, or publish.",
            "",
            f"Source mode: {self.source_mode}",
            f"Finding count: {len(self.findings)}",
            "",
        ]
        if self.live_fetches:
            lines.extend(["## Live inputs", ""])
            for item in self.live_fetches:
                status = item.status if item.status is not None else "n/a"
                outcome = "ok" if item.ok else "failed"
                lines.append(f"- {item.url}: {outcome} ({status}) - {item.summary}")
            lines.append("")

        if self.sources:
            lines.extend(["## Ground truth sources", ""])
            for source in self.sources:
                lines.append(f"- {source.product}: {source.mode} - {source.evidence}")
            lines.append("")

        lines.extend(["## Findings", ""])
        if not self.findings:
            lines.append("No deterministic drift found.")
            return "\n".join(lines).rstrip() + "\n"

        for index, finding in enumerate(self.findings, start=1):
            product = f" ({finding.product})" if finding.product else ""
            lines.extend(
                [
                    f"### {index}. {finding.code}{product} - {finding.severity}",
                    "",
                    f"- Location/file: {finding.location}",
                    f"- Current copy: {finding.current_copy}",
                    f"- Proposed copy: {finding.proposed_copy}",
                    f"- Evidence: {finding.evidence}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"


class TextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.parts.append(value)


def run_target_audit(
    target: str,
    root: Path,
    *,
    fetch_live: bool = True,
    product_roots: Sequence[Path] | None = None,
    portfolio_feed: Path | str | None = None,
    products: Sequence[str] = DEFAULT_PRODUCTS,
) -> AuditReport:
    root = root.resolve()
    normalized_target = target.strip().lower()
    if normalized_target in {"egbert", "egbert.io"}:
        return _run_egbert(root, fetch_live=fetch_live, portfolio_feed=portfolio_feed)
    if normalized_target in {"barglabs", "barglabs.ai", "barglabs-site"}:
        return _run_barglabs(
            root,
            fetch_live=fetch_live,
            product_roots=tuple(product_roots or ()),
            portfolio_feed=portfolio_feed,
            products=products,
        )
    raise ValueError(f"Unknown Aelfric target: {target}")


def _run_egbert(root: Path, *, fetch_live: bool, portfolio_feed: Path | str | None) -> AuditReport:
    site_hits = _collect_egbert_site_hits(root)
    live_fetches = tuple(_fetch_live_inputs(("https://egbert.io", "https://api.egbert.io/api/v1/health")) if fetch_live else ())
    sources, source_mode = _resolve_sources(
        root,
        product_roots=(),
        products=("egbert",),
        portfolio_feed=portfolio_feed,
        fallback_status_paths=(root / "STATUS.md",),
    )
    evidence_hits = list(_collect_egbert_evidence_hits(root))
    for source in sources:
        evidence_hits.extend(_hits_from_text(source.evidence, source.status_text))

    findings: list[Finding] = []
    findings.extend(_check_egbert_audit_export(root, site_hits))
    findings.extend(_check_wall_list(site_hits, target="egbert"))
    findings.extend(_check_egbert_capability_underclaims(tuple(evidence_hits), site_hits))
    findings.extend(_check_brand_voice(site_hits))

    return AuditReport(
        target="egbert",
        title="egbert.io sync proposal",
        generated_at=_now(),
        findings=tuple(_sort_findings(_dedupe_findings(findings))),
        sources=sources,
        live_fetches=live_fetches,
        source_mode=source_mode,
    )


def _run_barglabs(
    root: Path,
    *,
    fetch_live: bool,
    product_roots: Sequence[Path],
    portfolio_feed: Path | str | None,
    products: Sequence[str],
) -> AuditReport:
    site_hits = _collect_barglabs_site_hits(root)
    live_hits: tuple[TextHit, ...] = ()
    live_fetches: tuple[LiveFetch, ...] = ()
    if fetch_live:
        fetched = _fetch_site_text("https://barglabs.ai")
        live_fetches = (fetched[0],)
        if fetched[1]:
            live_hits = tuple(_hits_from_text("https://barglabs.ai", fetched[1]))
    all_hits = site_hits + live_hits
    sources, source_mode = _resolve_sources(
        root,
        product_roots=product_roots,
        products=products,
        portfolio_feed=portfolio_feed,
        fallback_status_paths=(),
    )

    findings: list[Finding] = []
    findings.extend(_check_wall_list(all_hits, target="barglabs"))
    findings.extend(_check_roster(all_hits))
    findings.extend(_check_barglabs_product_status(all_hits, sources, products))
    findings.extend(_check_links(site_hits, fetch_http=fetch_live))
    findings.extend(_check_thesis(all_hits))
    findings.extend(_check_brand_voice(all_hits))

    return AuditReport(
        target="barglabs",
        title="barglabs.ai sync proposal",
        generated_at=_now(),
        findings=tuple(_sort_findings(_dedupe_findings(findings))),
        sources=sources,
        live_fetches=live_fetches,
        source_mode=source_mode,
    )


def _collect_egbert_site_hits(root: Path) -> tuple[TextHit, ...]:
    site_root = root / "egbert-ui" / "src" / "pages"
    if not site_root.exists():
        return ()
    hits: list[TextHit] = []
    for pattern in ("*.tsx", "*.ts", "*.json", "*.md"):
        for path in sorted(site_root.glob(pattern)):
            if path.is_file() and path.name in EG_BERT_PUBLIC_FILES:
                hits.extend(_read_hits(path, root))
    return tuple(hits)


def _collect_barglabs_site_hits(root: Path) -> tuple[TextHit, ...]:
    hits: list[TextHit] = []
    for pattern in ("app/**/*.tsx", "app/**/*.ts", "app/**/*.mdx", "components/**/*.tsx", "components/**/*.ts"):
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                hits.extend(_read_hits(path, root))
    return tuple(hits)


def _collect_egbert_evidence_hits(root: Path) -> tuple[TextHit, ...]:
    candidates: list[Path] = []
    for relative in (
        "STATUS.md",
        "docs/audits",
        "docs/CHANGELOG",
        "docs/changelog",
        "egbert_core/db/migrations",
    ):
        path = root / relative
        if path.is_file():
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(sorted(item for item in path.rglob("*") if item.suffix in {".md", ".sql", ".py"}))
    for relative in (
        "egbert_core/api/routes/quant.py",
        "egbert_core/app/audit.py",
        "egbert_core/core/postgres_rls.py",
        "egbert_core/tenants/store.py",
        "egbert_core/tenants/execution_policy.py",
    ):
        path = root / relative
        if path.exists():
            candidates.append(path)
    hits: list[TextHit] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved not in seen and path.is_file():
            seen.add(resolved)
            hits.extend(_read_hits(path, root))
    return tuple(hits)


def _resolve_sources(
    root: Path,
    *,
    product_roots: Sequence[Path],
    products: Sequence[str],
    portfolio_feed: Path | str | None,
    fallback_status_paths: Sequence[Path],
) -> tuple[tuple[SourceEvidence, ...], str]:
    feed = portfolio_feed or os.environ.get("ALFRED_PORTFOLIO_FEED")
    if feed:
        feed_sources = _read_portfolio_feed(feed)
        if feed_sources:
            return feed_sources, "portfolio-feed"
    status_sources = _read_status_sources(root, product_roots, fallback_status_paths)
    return tuple(source for source in status_sources if _product_key(source.product) in {_product_key(p) for p in products}), "status-fallback"


def _read_portfolio_feed(feed: Path | str) -> tuple[SourceEvidence, ...]:
    try:
        text: str
        feed_label: str
        feed_value = str(feed)
        if feed_value.startswith(("http://", "https://")):
            request = urllib.request.Request(feed_value, headers={"User-Agent": "aelfric-site-sync/1.0"})
            with urllib.request.urlopen(request, timeout=12) as response:
                text = response.read(1_000_000).decode("utf-8", errors="replace")
            feed_label = feed_value
        else:
            path = Path(feed_value)
            if not path.exists():
                return ()
            text = path.read_text(encoding="utf-8")
            feed_label = str(path)
        data = json.loads(text)
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return ()

    products = data.get("products", data if isinstance(data, list) else [])
    if not isinstance(products, list):
        return ()
    sources: list[SourceEvidence] = []
    for item in products:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or item.get("productSlug") or item.get("name") or "").strip()
        if not slug:
            continue
        display = str(item.get("displayName") or item.get("productDisplayName") or slug)
        summary = str(item.get("status") or item.get("summary") or item.get("deployHealth", {}).get("summary", ""))
        pointers = item.get("sourcePointers") or item.get("sources") or []
        pointer_text = ", ".join(
            str(pointer.get("path") or pointer.get("url") or pointer.get("label"))
            for pointer in pointers
            if isinstance(pointer, dict)
        )
        evidence = f"{feed_label}: {pointer_text or display}"
        sources.append(SourceEvidence(product=canonical_product(slug), mode="portfolio-feed", evidence=evidence, status_text=summary))
    return tuple(sources)


def _read_status_sources(root: Path, product_roots: Sequence[Path], fallback_status_paths: Sequence[Path]) -> tuple[SourceEvidence, ...]:
    status_paths: list[Path] = []
    status_paths.extend(path for path in fallback_status_paths if path.exists())
    for product_root in product_roots:
        if not product_root.exists():
            continue
        if (product_root / "STATUS.md").exists():
            status_paths.append(product_root / "STATUS.md")
        status_paths.extend(sorted(product_root.glob("*/STATUS.md")))
    sources: list[SourceEvidence] = []
    seen: set[Path] = set()
    for status_path in status_paths:
        resolved = status_path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        product = "egbert" if status_path == root / "STATUS.md" else status_path.parent.name
        text = status_path.read_text(encoding="utf-8", errors="replace")
        sources.append(
            SourceEvidence(
                product=canonical_product(product),
                mode="status-fallback",
                evidence=_summarize_status_evidence(status_path, text),
                status_text=text,
            )
        )
    return tuple(sources)


def _check_egbert_audit_export(root: Path, site_hits: tuple[TextHit, ...]) -> list[Finding]:
    quant_path = root / "egbert_core" / "api" / "routes" / "quant.py"
    evidence = _quant_export_stub_evidence(quant_path, root)
    if evidence is None:
        return []
    findings: list[Finding] = []
    for hit in site_hits:
        if re.search(r"\baudit export\b|\bexport review-ready\b|\breview packets can be prepared\b", hit.line, re.I):
            findings.append(
                Finding(
                    code="audit-export-overclaim",
                    drift_class="OVERCLAIM",
                    severity="high",
                    location=hit.location,
                    current_copy=hit.line,
                    proposed_copy="Replace with copy that says audit evidence is captured server-side, but self-service audit export is not yet wired.",
                    evidence=evidence,
                    product="Egbert",
                )
            )
    return findings


def _quant_export_stub_evidence(path: Path, root: Path) -> str | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    in_export = False
    export_start = 0
    for index, line in enumerate(lines, start=1):
        if "def quant_export" in line:
            in_export = True
            export_start = index
        if in_export and ("return _stub(" in line or "response_model=QuantStubResponse" in line):
            relative = path.resolve().relative_to(root).as_posix()
            return f"{relative}:{index} quant_export returns QuantStubResponse/_stub (not_yet_wired; function starts at {relative}:{export_start})"
        if in_export and index > export_start + 60:
            break
    return None


CAPABILITY_RULES: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...], str], ...] = (
    (
        "hmac_append_only_audit",
        "HMAC append-only audit",
        (r"\bHMAC\b.*\baudit\b", r"\baudit\b.*\bHMAC\b", r"\bhmac-sha256-v2\b", r"\baudit hash chain\b"),
        (r"\bHMAC\b", r"\bhmac-sha256\b"),
        "Mention HMAC append-only audit evidence only in calm governance copy, with a code-backed citation.",
    ),
    (
        "postgres_rls",
        "Postgres RLS",
        (r"ENABLE ROW LEVEL SECURITY", r"\bCREATE POLICY\b.*\brls\b", r"\bpostgres_rls\b"),
        (r"\bPostgres RLS\b", r"\brow-level security\b", r"\brow level security\b"),
        "Mention Postgres row-level security as a tenant-isolation backstop, not as a broad compliance badge.",
    ),
    (
        "per_tenant_credential_isolation",
        "Per-tenant credential isolation",
        (r"\bper-tenant\b.*\bcredential", r"\bcredential\b.*\bper-tenant\b", r"\bencrypted_credentials\b", r"\bFernet\b.*\bcredentials\b", r"\bcredentials\b.*\bFernet\b"),
        (r"\bper-tenant credential", r"\bcredential isolation\b", r"\bencrypted broker credentials\b"),
        "Mention per-tenant credential isolation and encrypted broker credential handling where trust copy discusses custody.",
    ),
    (
        "execution_risk_gates",
        "Execution-risk gates",
        (r"\bexecution policy\b", r"\bpolicy-lockdown\b", r"\bpolicy lockdown\b", r"\bkill switch\b", r"\brisk gate"),
        (r"\bexecution-risk\b", r"\bexecution risk\b", r"\bpolicy-lockdown\b"),
        "Mention execution-risk gates as approval and policy controls, without implying live trading is broadly enabled.",
    ),
    (
        "monitoring_alerting",
        "Monitoring and alerting",
        (r"\bmonitoring\b.*\balert", r"\balert\b.*\bmonitoring\b", r"\bPrometheus\b", r"\balert canary\b", r"\bexternal uptime monitor"),
        (r"\bmonitoring\b", r"\balerting\b", r"\bPrometheus\b", r"\balert canary\b"),
        "Mention monitoring and alerting as operational evidence, keeping customer SLO claims out until approved.",
    ),
)


def _check_egbert_capability_underclaims(evidence_hits: tuple[TextHit, ...], site_hits: tuple[TextHit, ...]) -> list[Finding]:
    site_text = "\n".join(hit.line for hit in site_hits)
    findings: list[Finding] = []
    for capability_id, name, evidence_patterns, site_patterns, proposed_copy in CAPABILITY_RULES:
        evidence = _first_matching_hit(evidence_hits, evidence_patterns)
        if evidence is None:
            continue
        if any(re.search(pattern, site_text, re.I) for pattern in site_patterns):
            continue
        findings.append(
            Finding(
                code="capability-underclaim",
                drift_class="STALE_UNDERCLAIM",
                severity="medium",
                location="egbert-ui/src/pages/*",
                current_copy=f"No deterministic public-site mention of {name}.",
                proposed_copy=proposed_copy,
                evidence=f"{evidence.location} {evidence.line}",
                product="Egbert",
            )
        )
    return findings


WALL_LIST_RULES: tuple[tuple[str, str], ...] = (
    ("returns", r"\breturns\b|\breturn claim\b|\bperformance claim\b"),
    ("NAV", r"\bNAV\b|(?i:\bnet asset value\b)"),
    ("AUM", r"\bAUM\b|(?i:\bassets under management\b)"),
    (
        "customer",
        r"\bcustomer logos?\b|\bnamed customer\b|\bcustomers include\b|\bcustomer count\b|"
        r"\bcustomer traction\b|\bexternal customers\b|\bproduction customers\b|"
        r"\blive advisory customers\b|\bpaid customers\b",
    ),
    ("traction", r"\btraction\b"),
    ("SOC2", r"\bSOC\s*2\b|\bSOC2\b"),
    ("track-record", r"\btrack[- ]record\b"),
    ("pedigree", r"\bpedigree\b"),
)


def _check_wall_list(site_hits: tuple[TextHit, ...], *, target: str) -> list[Finding]:
    findings: list[Finding] = []
    for hit in site_hits:
        if _is_negative_wall_disclaimer(hit.line):
            continue
        for label, pattern in WALL_LIST_RULES:
            flags = 0 if label in {"NAV", "AUM"} else re.I
            if re.search(pattern, hit.line, flags):
                if label == "customer" and target == "barglabs" and _is_allowed_customer_zero_context(hit.line):
                    continue
                findings.append(
                    Finding(
                        code="wall-list-term",
                        drift_class="WALL_LIST",
                        severity="high",
                        location=hit.location,
                        current_copy=hit.line,
                        proposed_copy="Remove or replace wall-list language unless Houman approves a cited compliance-safe source.",
                        evidence="Wall-list constraint: no returns, NAV, AUM, customer, traction, SOC2, track-record, or pedigree claims.",
                    )
                )
    return findings


def _check_roster(site_hits: tuple[TextHit, ...]) -> list[Finding]:
    stale = {
        "Niels": "Niels has been removed from Barg Labs. Remove or replace this with current human-approved roster language.",
        "Amirali": "Amirali is a Wilfrid customer-zero student, not a Barg Labs team/cap-table member. Do not present him as team.",
    }
    findings: list[Finding] = []
    for hit in site_hits:
        for name, proposed in stale.items():
            if re.search(rf"\b{re.escape(name)}\b", hit.line):
                findings.append(
                    Finding(
                        code="roster-stale-name",
                        drift_class="ROSTER",
                        severity="high",
                        location=hit.location,
                        current_copy=hit.line,
                        proposed_copy=proposed,
                        evidence="Team roster instruction: Houman, Nima, Pooneh, and Carolynn are the human-approved roster; Niels is stale; Amirali is not team.",
                    )
                )
    return findings


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
}


def _check_barglabs_product_status(site_hits: tuple[TextHit, ...], sources: tuple[SourceEvidence, ...], products: Sequence[str]) -> list[Finding]:
    site_text = "\n".join(hit.line for hit in site_hits)
    mentioned = [canonical_product(product) for product in products if re.search(rf"\b{re.escape(product)}\b", site_text, re.I)]
    source_by_product = {_product_key(source.product): source for source in sources}
    findings: list[Finding] = []
    for product in mentioned:
        source = source_by_product.get(_product_key(product))
        if source is None:
            findings.append(
                Finding(
                    code="missing-product-evidence",
                    drift_class="SOURCE",
                    severity="medium",
                    location="product evidence",
                    current_copy=f"{product} appears in site copy.",
                    proposed_copy=f"Flag {product} for human judgment until STATUS.md or Alfred operator-summary evidence is available.",
                    evidence=f"No reachable STATUS.md or Alfred portfolio source for {product}.",
                    product=product,
                )
            )
            continue
        for hit in _lines_for_product(site_hits, product):
            overclaim = _product_overclaim(product, hit.line, source.status_text)
            if overclaim:
                findings.append(
                    Finding(
                        code="product-status-drift",
                        drift_class="PRODUCT_STATUS",
                        severity="high",
                        location=hit.location,
                        current_copy=hit.line,
                        proposed_copy=_proposed_status_copy(product, source.status_text),
                        evidence=source.evidence,
                        product=product,
                    )
                )
                break
    return findings


def _check_links(site_hits: tuple[TextHit, ...], *, fetch_http: bool) -> list[Finding]:
    expected_links = {
        "Egbert": "https://egbert.io",
        "Alfred": "https://alfred.barglabs.ai/mission-control",
        "Therasyn": "https://therasyn.ai",
        "Edwy": "https://edwy.barglabs.ai",
    }
    findings: list[Finding] = []
    for hit in site_hits:
        for href in re.findall(r"href=[\"']([^\"']+)[\"']", hit.line):
            if href == "#":
                findings.append(
                    Finding(
                        code="dead-or-self-link",
                        drift_class="LINKS",
                        severity="medium",
                        location=hit.location,
                        current_copy='href="#"',
                        proposed_copy="Use a real section id, product URL, mailto link, or remove the link.",
                        evidence="Self-links are not useful CTAs for barglabs.ai sync.",
                    )
                )
            elif fetch_http and href.startswith("http"):
                findings.extend(_check_http_link(hit.location, href))
        for product, expected_href in expected_links.items():
            if product.lower() in hit.line.lower() and "href=" in hit.line and expected_href not in hit.line:
                findings.append(
                    Finding(
                        code="wrong-product-link",
                        drift_class="LINKS",
                        severity="medium",
                        location=hit.location,
                        current_copy=f"{product} appears without expected link {expected_href}.",
                        proposed_copy=f"Point {product} CTA/card link to {expected_href} or flag why it is intentionally absent.",
                        evidence=f"Expected product URL mapping: {product} -> {expected_href}.",
                        product=product,
                    )
                )
    return findings


def _check_http_link(location: str, href: str) -> list[Finding]:
    request = urllib.request.Request(href, headers={"User-Agent": "aelfric-site-sync/1.0"}, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return [
            Finding(
                code="dead-or-wrong-link",
                drift_class="LINKS",
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
                drift_class="LINKS",
                severity="medium",
                location=location,
                current_copy=href,
                proposed_copy="Replace or remove this product/CTA link.",
                evidence=f"HTTP HEAD returned {status}.",
            )
        ]
    return []


def _check_thesis(site_hits: tuple[TextHit, ...]) -> list[Finding]:
    phrases = ("all ten products are live", "shared substrate for all ten products", "every product runs on alfred", "fully live substrate")
    findings: list[Finding] = []
    for hit in site_hits:
        lowered = hit.line.lower()
        for phrase in phrases:
            if phrase in lowered:
                findings.append(
                    Finding(
                        code="substrate-thesis-overclaim",
                        drift_class="THESIS",
                        severity="medium",
                        location=hit.location,
                        current_copy=hit.line,
                        proposed_copy="Lead with Alfred Console as live and describe the broader L4/L5 substrate as partly aspirational until Alfred operator-summary evidence proves otherwise.",
                        evidence="ADR-0001: Alfred is the conductor consuming product report-ups; products remain standalone and not all products are proven live on a shared substrate.",
                    )
                )
    return findings


def _check_brand_voice(site_hits: tuple[TextHit, ...]) -> list[Finding]:
    rules = (
        ("brand-voice-emoji", r"[\U0001F300-\U0001FAFF]", "Remove emoji. Public product copy should stay calm and quiet."),
        ("brand-voice-ai-os", r"\bAI[- ]OS\b", "Avoid AI-OS positioning; lead with sovereign/on-prem governance and operator report-up."),
        ("brand-voice-moment", r"\bMoment\b", "Do not imitate competitor Moment framing; use Barg Labs governance and sovereignty wedge."),
        ("brand-voice-hype", r"\b(revolutionary|crush|dominate|guaranteed|10x|moonshot)\b", "Use calm, evidence-backed language."),
    )
    findings: list[Finding] = []
    for hit in site_hits:
        for code, pattern, proposed in rules:
            if re.search(pattern, hit.line, re.I):
                findings.append(
                    Finding(
                        code=code,
                        drift_class="GTM_BRAND",
                        severity="low",
                        location=hit.location,
                        current_copy=hit.line,
                        proposed_copy=proposed,
                        evidence=f"Heuristic brand rule: {code}.",
                    )
                )
    return findings


def _read_hits(path: Path, root: Path) -> list[TextHit]:
    text = path.read_text(encoding="utf-8", errors="replace")
    relative = path.resolve().relative_to(root).as_posix()
    return list(_hits_from_text(relative, text))


def _hits_from_text(path: str, text: str) -> list[TextHit]:
    hits: list[TextHit] = []
    for index, line in enumerate(text.splitlines(), start=1):
        cleaned = _clean_line(line)
        if cleaned:
            hits.append(TextHit(path=path, line_number=index, line=cleaned))
    return hits


def _fetch_live_inputs(urls: Sequence[str]) -> list[LiveFetch]:
    fetches: list[LiveFetch] = []
    for url in urls:
        fetch, _ = _fetch_site_text(url)
        fetches.append(fetch)
    return fetches


def _fetch_site_text(url: str) -> tuple[LiveFetch, str]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "aelfric-site-sync/1.0"})
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read(1_000_000)
            status = int(response.status)
            text = body.decode("utf-8", errors="replace")
            if url.endswith("/health"):
                summary = _summarize_health(text)
                return LiveFetch(url=url, ok=True, status=status, summary=summary), text
            parser = TextExtractor()
            parser.feed(text)
            extracted = "\n".join(parser.parts)
            return LiveFetch(url=url, ok=True, status=status, summary=_clean_line(extracted[:300])), extracted
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return LiveFetch(url=url, ok=False, status=None, summary=str(exc)), ""


def _summarize_health(text: str) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _clean_line(text[:300])
    if not isinstance(data, dict):
        return _clean_line(text[:300])
    return f"health fields: {', '.join(sorted(str(key) for key in data.keys())[:12])}"


def _first_matching_hit(hits: tuple[TextHit, ...] | list[TextHit], patterns: Iterable[str]) -> TextHit | None:
    for hit in hits:
        for pattern in patterns:
            if re.search(pattern, hit.line, re.I):
                return hit
    return None


def _lines_for_product(site_hits: tuple[TextHit, ...], product: str) -> list[TextHit]:
    return [hit for hit in site_hits if re.search(rf"\b{re.escape(product)}\b", hit.line, re.I)]


def _product_overclaim(product: str, copy: str, status_text: str) -> bool:
    expectation = PRODUCT_EXPECTATIONS.get(product, {})
    copy_lower = copy.lower()
    status_lower = status_text.lower()
    overclaim_terms = expectation.get("overclaim_terms", ())
    if not any(term in copy_lower for term in overclaim_terms):
        return False
    allowed_terms = expectation.get("allowed_status_terms", ())
    return bool(not allowed_terms or any(term in status_lower for term in allowed_terms))


def _proposed_status_copy(product: str, status_text: str) -> str:
    status_lower = status_text.lower()
    if product == "Egbert" and "paper" in status_lower:
        return "Describe Egbert as governed paper-pilot infrastructure; do not imply production/live trading, returns, NAV, AUM, or customer traction."
    if product == "Alfred" and ("console" in status_lower or "mission" in status_lower):
        return "Describe Alfred as Console/operator surface live, without implying all portfolio products run on a completed substrate."
    if product == "Therasyn" and ("parked" in status_lower or "md" in status_lower):
        return "Describe Therasyn as parked/pending MD co-founder or clinical governance thesis work; do not imply live health-system production."
    return f"Align {product} wording to cited STATUS or Alfred operator-summary evidence; flag uncertain positioning for human review."


def _summarize_status_evidence(status_path: Path, status_text: str) -> str:
    markers = ("one-line state", "phase", "paper", "pilot", "mvp", "parked", "no paying", "no signed", "no live deployment", "blocked")
    for line in status_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("|") and not stripped.startswith("#") and len(stripped) < 260:
            if any(marker in stripped.lower() for marker in markers):
                return f"{status_path}: {stripped}"
    for line in status_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("|") and len(stripped) < 260:
            return f"{status_path}: {stripped}"
    return f"{status_path}: STATUS.md present."


def _is_negative_wall_disclaimer(line: str) -> bool:
    lowered = line.lower()
    return any(
        marker in lowered
        for marker in (
            "no return",
            "no returns",
            "not promises of live returns",
            "not a promise of returns",
            "not customer logos",
            "no customer logos",
            "wall-list",
            "do not",
            "never",
            "remove",
        )
    )


def _is_allowed_customer_zero_context(line: str) -> bool:
    return "customer-zero" in line.lower()


def _dedupe_findings(findings: Iterable[Finding]) -> list[Finding]:
    deduped: list[Finding] = []
    seen: set[tuple[str, str, str, str | None]] = set()
    for finding in findings:
        key = (finding.code, finding.location, finding.current_copy, finding.product)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _sort_findings(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda item: (_severity_rank(item.severity), item.code, item.location))


def _severity_rank(severity: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(severity, 3)


def _clean_line(value: str) -> str:
    return " ".join(value.strip().split())


def _product_key(name: str) -> str:
    normalized = name.strip().lower().replace("_", "-")
    for canonical, aliases in PRODUCT_ALIASES.items():
        if normalized in aliases:
            return canonical
    return normalized


def canonical_product(name: str) -> str:
    key = _product_key(name)
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


def _now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
