from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from aelfric_site_sync import run_target_audit


class AelfricSiteSyncTests(unittest.TestCase):
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

        report = run_target_audit(
            "barglabs",
            root,
            fetch_live=False,
            product_roots=[root / "products"],
        )

        codes = {finding.code for finding in report.findings}
        self.assertIn("roster-stale-name", codes)
        self.assertIn("wall-list-term", codes)
        self.assertTrue(any("Niels" in finding.current_copy for finding in report.findings))
        self.assertTrue(any("returns" in finding.current_copy.lower() for finding in report.findings))

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

        report = run_target_audit(
            "barglabs",
            root,
            fetch_live=False,
            product_roots=[root / "products"],
        )

        drift = [finding for finding in report.findings if finding.code == "product-status-drift"]
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

        report = run_target_audit(
            "barglabs",
            root,
            fetch_live=False,
            product_roots=[root / "products"],
        )

        missing = [finding for finding in report.findings if finding.code == "missing-product-evidence"]
        self.assertEqual(1, len(missing))
        self.assertEqual("Therasyn", missing[0].product)
        self.assertIn("human judgment", missing[0].proposed_copy)

    def test_portfolio_feed_is_preferred_over_status_fallback(self) -> None:
        root = self.make_workspace(
            """
            const products = [{
              name: "Alfred",
              body: "Alfred is the live Console for operators.",
            }];
            """,
            {"alfred": "Stale local STATUS says Alfred is blocked."},
        )
        feed = root / "portfolio-feed.json"
        feed.write_text(
            json.dumps(
                {
                    "products": [
                        {
                            "slug": "alfred",
                            "displayName": "Alfred",
                            "status": "Console live; operator summary aggregation active",
                            "sourcePointers": [{"path": "alfred/operator-summary.json"}],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        report = run_target_audit(
            "barglabs",
            root,
            fetch_live=False,
            product_roots=[root / "products"],
            portfolio_feed=feed,
        )

        self.assertEqual("portfolio-feed", report.source_mode)
        self.assertTrue(any("alfred/operator-summary.json" in source.evidence for source in report.sources))

    def test_report_contains_issue_proposal_shape(self) -> None:
        root = self.make_workspace(
            """
            export default function Page() {
              return <main>Niels helps customers see AUM.</main>;
            }
            """,
            {},
        )
        report = run_target_audit(
            "barglabs",
            root,
            fetch_live=False,
            product_roots=[root / "products"],
        )

        markdown = report.to_markdown()

        self.assertIn("# barglabs.ai sync proposal", markdown)
        self.assertIn("## Findings", markdown)
        self.assertIn("Location/file", markdown)
        self.assertIn("Evidence", markdown)

    def test_weekly_workflow_is_issue_only_and_least_privilege(self) -> None:
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/site-sync.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("contents: read", workflow)
        self.assertIn("issues: write", workflow)
        self.assertNotIn("pull-requests:", workflow)
        self.assertNotIn("git commit", workflow)
        self.assertNotIn("git push", workflow)
        self.assertNotIn("gh pr", workflow)
        self.assertNotIn("actions/create-github-app-token", workflow)


if __name__ == "__main__":
    unittest.main()
