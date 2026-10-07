"""Unit and integration test suite for Poppy CLI."""

import unittest
import json
import subprocess
import sys
from pathlib import Path
from poppy.boards import list_boards, load_local_graph, render_board_tree, export_board_markdown
from poppy.reviews import get_reviews_summary, filter_reviews, filter_questions, load_deal_data, get_deal_tiers
from poppy.diagnose import run_diagnostics, render_diagnostics_report

class TestPoppyCLI(unittest.TestCase):

    def test_list_boards(self):
        boards = list_boards()
        self.assertGreaterEqual(len(boards), 2)
        b0 = next((b for b in boards if b.id == "polished-sea-2LmlU"), None)
        self.assertIsNotNone(b0)
        self.assertEqual(b0.name, "Ivory Antelope")
        self.assertEqual(b0.node_count, 26)
        self.assertEqual(b0.edge_count, 5)

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

    def test_diagnostics_pass(self):
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

        # Check explicit verified details
        self.assertIn("Clerk Auth valid", check_map["Clerk Authentication"]["details"])
        self.assertIn("Firebase auth token valid", check_map["Firebase Custom Auth"]["details"])
        self.assertIn("Firestore 200", check_map["Google Firestore Gateway"]["details"])
        self.assertIn("AppSumo ledger cached", check_map["AppSumo Intelligence Archive"]["details"])
        self.assertIn(">100KB", check_map["E2E Visual Screenshots Audit"]["details"])

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

        # diagnose
        res = subprocess.run([sys.executable, str(bin_path), "diagnose"], capture_output=True, text=True, check=True)
        self.assertIn("Overall Status: PASS", res.stdout)
        self.assertIn("Verified Status: Firestore 200 ✓", res.stdout)

if __name__ == "__main__":
    unittest.main()
