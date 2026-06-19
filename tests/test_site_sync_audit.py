import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.site_sync_audit import (
    AuditConfig,
    collect_findings,
    render_report,
)


class SiteSyncAuditTests(unittest.TestCase):
    def make_workspace(self, site_copy: str, statuses: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp())
        app = root / "app"
        app.mkdir()
        (app / "page.tsx").write_text(site_copy, encoding="utf-8")
        products = root / "products"
        products.mkdir()
        for product, status in statuses.items():
            repo = products / product
            repo.mkdir()
            (repo / "STATUS.md").write_text(status, encoding="utf-8")
        return root

    def test_flags_removed_people_and_wall_list_terms(self) -> None:
        root = self.make_workspace(
            """
            export default function Page() {
              return <main>Niels helps customers see AUM and returns.</main>;
            }
            """,
            {},
        )

        findings = collect_findings(
            AuditConfig(site_root=root, product_roots=[root / "products"], check_live=False)
        )

        codes = {finding.code for finding in findings}
        self.assertIn("roster-stale-name", codes)
        self.assertIn("wall-list-term", codes)
        self.assertTrue(any("Niels" in finding.current_copy for finding in findings))
        self.assertTrue(any("returns" in finding.current_copy.lower() for finding in findings))

    def test_detects_product_status_overclaim_against_status_file(self) -> None:
        root = self.make_workspace(
            """
            const products = [{
              name: "Egbert",
              body: "Egbert is live production trading infrastructure with customer traction.",
            }];
            """,
            {
                "egbert": textwrap.dedent(
                    """
                    # Egbert Status

                    **Phase:** institutional B2B trading infrastructure; paper-mode founder dogfooding;
                    Pilot 1 target mid-Sep 2026.
                    Safety walls: no return/NAV/drawdown/broker-performance claim.
                    """
                )
            },
        )

        findings = collect_findings(
            AuditConfig(site_root=root, product_roots=[root / "products"], check_live=False)
        )

        drift = [finding for finding in findings if finding.code == "product-status-drift"]
        self.assertEqual(1, len(drift))
        self.assertEqual("Egbert", drift[0].product)
        self.assertIn("paper-mode", drift[0].evidence)
        self.assertIn("production", drift[0].current_copy)

    def test_missing_status_evidence_is_flagged_for_human_judgment(self) -> None:
        root = self.make_workspace(
            """
            const products = [{
              name: "Therasyn",
              body: "Therasyn is governance infrastructure for clinical AI.",
            }];
            """,
            {},
        )

        findings = collect_findings(
            AuditConfig(site_root=root, product_roots=[root / "products"], check_live=False)
        )

        missing = [finding for finding in findings if finding.code == "missing-product-evidence"]
        self.assertEqual(1, len(missing))
        self.assertEqual("Therasyn", missing[0].product)
        self.assertIn("human judgment", missing[0].proposed_copy)

    def test_report_contains_issue_proposal_shape(self) -> None:
        root = self.make_workspace(
            """
            export default function Page() {
              return <main>Niels helps customers see AUM.</main>;
            }
            """,
            {},
        )
        findings = collect_findings(
            AuditConfig(site_root=root, product_roots=[root / "products"], check_live=False)
        )

        report = render_report(findings)

        self.assertIn("# barglabs.ai Sync Proposal", report)
        self.assertIn("## Findings", report)
        self.assertIn("Location", report)
        self.assertIn("Evidence", report)


if __name__ == "__main__":
    unittest.main()
