"""Unit and integration test suite for Poppy CLI."""

import unittest
from unittest.mock import patch, MagicMock
import urllib.error
import os
import base64
import json
import subprocess
import sys
from pathlib import Path
from poppy.boards import list_boards, load_local_graph, render_board_tree, export_board_markdown
from poppy.reviews import get_reviews_summary, filter_reviews, filter_questions, load_deal_data, get_deal_tiers
from poppy.diagnose import run_diagnostics, render_diagnostics_report

def make_mock_jwt(header: dict, payload: dict) -> str:
    def b64url(d: dict) -> str:
        s = json.dumps(d).encode("utf-8")
        return base64.urlsafe_b64encode(s).decode("ascii").rstrip("=")
    return f"{b64url(header)}.{b64url(payload)}.mock_sig"

class MockHTTPResponse:
    def __init__(self, status=200):
        self.status = status
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class TestPoppyCLI(unittest.TestCase):

    def test_list_boards(self):
        boards = list_boards()
        self.assertGreaterEqual(len(boards), 2)
        b0 = next((b for b in boards if b.id == "polished-sea-2LmlU"), None)
        self.assertIsNotNone(b0)
        self.assertEqual(b0.name, "Ivory Antelope")
        self.assertEqual(b0.node_count, 26)
        self.assertEqual(b0.edge_count, 5)

    def test_dynamic_board_discovery(self):
        base_dir = Path(__file__).resolve().parent.parent
        mock_file = base_dir / "board_mock_discovery_test.json"
        try:
            mock_file.write_text(json.dumps({
                "boardId": "mock-discovery-test",
                "name": "Mock Discovered Canvas",
                "nodes": [
                    {"id": "n1", "type": "textNode", "title": "Node 1", "data": {"userName": "Test Creator", "userEmail": "creator@example.com"}}
                ],
                "edges": []
            }))
            boards = list_boards()
            discovered = next((b for b in boards if b.id == "mock-discovery-test"), None)
            self.assertIsNotNone(discovered)
            self.assertEqual(discovered.name, "Mock Discovered Canvas")
            self.assertEqual(discovered.owner_name, "Test Creator")
            self.assertEqual(discovered.node_count, 1)
            self.assertEqual(discovered.edge_count, 0)
        finally:
            if mock_file.exists():
                mock_file.unlink()

    def test_load_graph(self):
        graph = load_local_graph("polished-sea-2LmlU")
        self.assertIsNotNone(graph)
        self.assertEqual(graph.graph_id, "BNW7aGRhauOFL1L5SKFi")
        self.assertEqual(len(graph.nodes), 26)
        self.assertEqual(len(graph.edges), 5)

        # Verify node types
        types = {n.type for n in graph.nodes}
        self.assertIn("groupNode", types)
        self.assertIn("chatNode", types)
        self.assertIn("youtubeNode", types)

        # Verify tree rendering shows correct Graph ID and connections
        tree = render_board_tree(graph)
        self.assertIn("Graph ID: BNW7aGRhauOFL1L5SKFi", tree)
        self.assertIn("Functional Groups", tree)
        self.assertIn("AI Chat Hubs", tree)
        self.assertIn("Synthesizing Context From", tree)

    def test_export_markdown(self):
        graph = load_local_graph("polished-sea-2LmlU")
        md = export_board_markdown(graph)
        self.assertIn("# Poppy AI Board: polished-sea-2LmlU", md)
        self.assertIn("> **Graph ID**: `BNW7aGRhauOFL1L5SKFi`", md)
        self.assertIn("## Canvas Nodes", md)
        self.assertIn("## Connections & Data Flow", md)

    def test_export_json(self):
        graph = load_local_graph("polished-sea-2LmlU")
        payload = {
            "board_id": graph.board_id,
            "graph_id": graph.graph_id,
            "nodes": [n.__dict__ for n in graph.nodes],
            "edges": [e.__dict__ for e in graph.edges]
        }
        self.assertEqual(payload["graph_id"], "BNW7aGRhauOFL1L5SKFi")
        self.assertEqual(len(payload["nodes"]), 26)
        self.assertEqual(len(payload["edges"]), 5)
        self.assertEqual(payload["edges"][0]["edge_type"], "connectionEdge")
        self.assertEqual(payload["edges"][0]["target_handle"], "chat-connector")

    def test_reviews_summary(self):
        summary = get_reviews_summary()
        self.assertEqual(summary["total_reviews"], 161)
        self.assertAlmostEqual(summary["average_tacos"], 4.83, places=1)
        self.assertEqual(summary["distribution"][5], 153)
        self.assertEqual(summary["distribution"][1], 5)
        # Deep assertion: both title and comment are scanned for sentiment
        self.assertGreater(summary["positive_mentions"], 30)
        self.assertGreater(summary["critique_mentions"], 30)

    def test_filter_reviews(self):
        reviews = filter_reviews(limit=5, min_rating=5)
        self.assertEqual(len(reviews), 5)
        for r in reviews:
            self.assertEqual(r["rating"], 5)
            self.assertNotEqual(r["name"], "Anonymous")
            self.assertTrue(len(r["name"]) > 0)
            self.assertTrue(len(r["content"]) > 20)
            self.assertTrue(len(r["date"]) == 10)  # YYYY-MM-DD
            self.assertTrue(len(r["title"]) > 0)

        # Check first review specifically
        r0 = reviews[0]
        self.assertEqual(r0["name"], "drummersgabe")
        self.assertEqual(r0["date"], "2026-06-08")
        self.assertIn("creative tasks", r0["content"])

    def test_filter_reviews_boundary_zero(self):
        """Boundary test: limit 0 and negative limit must return empty list."""
        self.assertEqual(filter_reviews(limit=0), [])
        self.assertEqual(filter_reviews(limit=-1), [])
        self.assertEqual(filter_reviews(limit=-100), [])

    def test_filter_questions(self):
        questions = filter_questions(limit=5)
        self.assertEqual(len(questions), 5)
        for q in questions:
            self.assertNotEqual(q["author"], "")
            self.assertTrue(len(q["question"]) > 10)
            self.assertGreaterEqual(q["answer_count"], 1)
            self.assertNotEqual(q["founder_reply"], "No reply")

        # Check first question specifically
        q0 = questions[0]
        self.assertEqual(q0["author"], "drummersgabe")
        self.assertIn("power user plan", q0["question"].lower())
        self.assertIn("Amaanath_PoppyAI", q0["founder_reply"])

    def test_filter_questions_boundary_zero(self):
        """Boundary test: limit 0 and negative limit must return empty list."""
        self.assertEqual(filter_questions(limit=0), [])
        self.assertEqual(filter_questions(limit=-1), [])
        self.assertEqual(filter_questions(limit=-100), [])

    def test_tiers_matrix(self):
        tiers = get_deal_tiers()
        self.assertEqual(len(tiers), 6)
        
        # Verify no "N/A" values
        for t in tiers:
            self.assertNotIn("N/A", t["credits_per_month"])
            self.assertNotIn("N/A", t["brands_limit"])
            self.assertNotIn("N/A", t["seats_limit"])
            self.assertTrue(t["price"].startswith("$"))

        # Verify Tier 1
        t1 = tiers[0]
        self.assertEqual(t1["tier"], 1)
        self.assertEqual(t1["price"], "$279")
        self.assertEqual(t1["credits_per_month"], "500/mo")
        self.assertEqual(t1["brands_limit"], "3 Brands")

        # Verify Tier 4 has BYOK
        t4 = tiers[3]
        self.assertEqual(t4["tier"], 4)
        self.assertEqual(t4["price"], "$1,379")
        self.assertIn("BYOK", t4["key_perks"])

        # Verify Tier 5 has API
        t5 = tiers[4]
        self.assertEqual(t5["tier"], 5)
        self.assertEqual(t5["price"], "$2,259")
        self.assertIn("API", t5["key_perks"])

        # Verify Tier 6 has White-Label & Unlimited Brands
        t6 = tiers[5]
        self.assertEqual(t6["tier"], 6)
        self.assertEqual(t6["price"], "$4,459")
        self.assertEqual(t6["brands_limit"], "Unlimited Brands")
        self.assertIn("White-Label", t6["key_perks"])

    @patch("urllib.request.urlopen", return_value=MockHTTPResponse(200))
    @patch.dict(os.environ, {
        "CLERK_TOKEN": make_mock_jwt({"alg": "RS256", "typ": "JWT"}, {"sub": "user_test", "sid": "sess_test"}),
        "FIREBASE_AUTH_TOKEN": make_mock_jwt({"alg": "RS256", "typ": "JWT"}, {"uid": "user_test"})
    })
    def test_diagnostics_pass(self, _mock_url):
        diag = run_diagnostics()
        self.assertEqual(diag["overall_status"], "PASS")
        self.assertIsNotNone(diag["timestamp"])
        
        check_map = {c["name"]: c for c in diag["checks"]}
        self.assertIn("Python Runtime", check_map)
        self.assertIn("E2E Visual Screenshots Audit", check_map)
        self.assertIn("Local Board Graph Cache", check_map)
        self.assertIn("AppSumo Intelligence Archive", check_map)
        self.assertIn("Clerk Authentication", check_map)
        self.assertIn("Firebase Custom Auth", check_map)
        self.assertIn("Google Firestore Gateway", check_map)
        self.assertIn("Poppy AI Web Edge", check_map)

        # Check genuine validated details
        self.assertIn("Valid Clerk JWT", check_map["Clerk Authentication"]["details"])
        self.assertIn("Valid Firebase JWT", check_map["Firebase Custom Auth"]["details"])
        self.assertIn("Firestore 200", check_map["Google Firestore Gateway"]["details"])
        self.assertIn("AppSumo ledger cached", check_map["AppSumo Intelligence Archive"]["details"])
        self.assertIn(">100KB", check_map["E2E Visual Screenshots Audit"]["details"])

        # Dynamic banner check
        rep = render_diagnostics_report(diag)
        self.assertIn("Verified Status: Firestore 200 ✓ | Clerk Auth valid ✓ | Firebase auth token ✓ | AppSumo ledger cached ✓", rep)

    @patch("urllib.request.urlopen", return_value=MockHTTPResponse(200))
    @patch.dict(os.environ, {}, clear=True)
    def test_diagnostics_unconfigured_warn(self, _mock_url):
        diag = run_diagnostics()
        self.assertEqual(diag["overall_status"], "WARN")
        rep = render_diagnostics_report(diag)
        self.assertIn("Clerk Auth unconfigured ⚠", rep)
        self.assertIn("Firebase auth unconfigured ⚠", rep)

    @patch("urllib.request.urlopen", side_effect=Exception("Connection refused"))
    def test_diagnostics_offline_failure(self, _mock_url):
        diag = run_diagnostics()
        self.assertEqual(diag["overall_status"], "FAIL")
        rep = render_diagnostics_report(diag)
        self.assertIn("Firestore Unreachable ✗", rep)
        self.assertNotIn("Firestore 200 ✓", rep)

    @patch("urllib.request.urlopen", return_value=MockHTTPResponse(200))
    @patch.dict(os.environ, {"CLERK_TOKEN": "malformed_token_not_jwt"})
    def test_diagnostics_malformed_token(self, _mock_url):
        diag = run_diagnostics()
        self.assertEqual(diag["overall_status"], "FAIL")
        rep = render_diagnostics_report(diag)
        self.assertIn("Clerk Auth invalid ✗", rep)

    def test_render_diagnostics_report_dynamic_footer(self):
        diag_healthy = {
            "timestamp": "2026-10-07T12:00:00Z",
            "overall_status": "PASS",
            "checks": [
                {"name": "Google Firestore Gateway", "status": "PASS", "details": "Firestore 200 connected"},
                {"name": "Clerk Authentication", "status": "PASS", "details": "Valid"},
                {"name": "Firebase Custom Auth", "status": "PASS", "details": "Valid"},
                {"name": "AppSumo Intelligence Archive", "status": "PASS", "details": "Cached"},
            ]
        }
        report_healthy = render_diagnostics_report(diag_healthy)
        self.assertIn("Firestore 200 ✓", report_healthy)
        self.assertIn("Clerk Auth valid ✓", report_healthy)
        self.assertIn("Firebase auth token ✓", report_healthy)
        self.assertIn("AppSumo ledger cached ✓", report_healthy)

        diag_outage = {
            "timestamp": "2026-10-07T12:00:00Z",
            "overall_status": "FAIL",
            "checks": [
                {"name": "Google Firestore Gateway", "status": "FAIL", "details": "Unreachable"},
                {"name": "Clerk Authentication", "status": "PASS", "details": "Valid"},
                {"name": "Firebase Custom Auth", "status": "PASS", "details": "Valid"},
                {"name": "AppSumo Intelligence Archive", "status": "PASS", "details": "Cached"},
            ]
        }
        report_outage = render_diagnostics_report(diag_outage)
        self.assertNotIn("Firestore 200 ✓", report_outage)
        self.assertIn("Firestore Unreachable ✗", report_outage)
        self.assertIn("Overall Status: FAIL", report_outage)

    def test_cli_execution_e2e(self):
        base_dir = Path(__file__).resolve().parent.parent
        bin_path = base_dir / "bin" / "poppy"

        # boards list
        res = subprocess.run([sys.executable, str(bin_path), "boards", "list", "--json"], capture_output=True, text=True, check=True)
        boards = json.loads(res.stdout)
        self.assertGreaterEqual(len(boards), 2)

        # boards get
        res = subprocess.run([sys.executable, str(bin_path), "boards", "get", "polished-sea-2LmlU"], capture_output=True, text=True, check=True)
        self.assertIn("Graph ID: BNW7aGRhauOFL1L5SKFi", res.stdout)

        # boards export json
        res = subprocess.run([sys.executable, str(bin_path), "boards", "export", "polished-sea-2LmlU", "--format", "json"], capture_output=True, text=True, check=True)
        exp = json.loads(res.stdout)
        self.assertEqual(exp["graph_id"], "BNW7aGRhauOFL1L5SKFi")
        self.assertEqual(len(exp["nodes"]), 26)
        self.assertEqual(len(exp["edges"]), 5)

        # tiers json
        res = subprocess.run([sys.executable, str(bin_path), "tiers", "--json"], capture_output=True, text=True, check=True)
        tiers = json.loads(res.stdout)
        self.assertEqual(len(tiers), 6)

        # reviews list --limit 0
        res = subprocess.run([sys.executable, str(bin_path), "reviews", "list", "--limit", "0", "--json"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(res.stdout), [])

        res_txt = subprocess.run([sys.executable, str(bin_path), "reviews", "list", "--limit", "0"], capture_output=True, text=True, check=True)
        self.assertIn("Found 0 reviews (limit: 0)", res_txt.stdout)

        # questions list --limit 0
        res = subprocess.run([sys.executable, str(bin_path), "questions", "list", "--limit", "0", "--json"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(res.stdout), [])

        res_txt = subprocess.run([sys.executable, str(bin_path), "questions", "list", "--limit", "0"], capture_output=True, text=True, check=True)
        self.assertIn("Found 0 Q&A threads (limit: 0)", res_txt.stdout)

        # diagnose in default environment
        res_default = subprocess.run([sys.executable, str(bin_path), "diagnose"], capture_output=True, text=True, check=True)
        self.assertIn("POPPY AI DIAGNOSTIC AUDIT REPORT", res_default.stdout)
        self.assertIn("Audit Timestamp:", res_default.stdout)
        self.assertIn("Verified Status:", res_default.stdout)

        # diagnose with mock authenticated environment
        mock_env = os.environ.copy()
        mock_env["CLERK_TOKEN"] = make_mock_jwt({"alg": "RS256", "typ": "JWT"}, {"sub": "user_test"})
        mock_env["FIREBASE_AUTH_TOKEN"] = make_mock_jwt({"alg": "RS256", "typ": "JWT"}, {"uid": "user_test"})
        res = subprocess.run([sys.executable, str(bin_path), "diagnose"], capture_output=True, text=True, check=True, env=mock_env)
        self.assertIn("Overall Status: PASS", res.stdout)
        self.assertIn("Verified Status: Firestore 200 ✓", res.stdout)
        self.assertIn("Clerk Auth valid ✓", res.stdout)
        self.assertIn("Firebase auth token ✓", res.stdout)
        self.assertIn("AppSumo ledger cached ✓", res.stdout)

        # diagnose --json with mock authenticated environment
        res_json = subprocess.run([sys.executable, str(bin_path), "diagnose", "--json"], capture_output=True, text=True, check=True, env=mock_env)
        diag_json = json.loads(res_json.stdout)
        self.assertEqual(diag_json["overall_status"], "PASS")
        self.assertIn("checks", diag_json)
        self.assertEqual(len(diag_json["checks"]), 8)

if __name__ == "__main__":
    unittest.main()
