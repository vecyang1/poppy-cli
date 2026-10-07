"""Unit and integration test suite for Poppy CLI."""

import unittest
import json
from pathlib import Path
from poppy.boards import list_boards, load_local_graph, render_board_tree, export_board_markdown
from poppy.reviews import get_reviews_summary, filter_reviews, filter_questions, load_deal_data
from poppy.diagnose import run_diagnostics

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
        self.assertEqual(len(graph.nodes), 26)
        self.assertEqual(len(graph.edges), 5)

        # Verify node types
        types = {n.type for n in graph.nodes}
        self.assertIn("groupNode", types)
        self.assertIn("chatNode", types)
        self.assertIn("youtubeNode", types)

        # Verify connections
        tree = render_board_tree(graph)
        self.assertIn("Functional Groups", tree)
        self.assertIn("AI Chat Hubs", tree)
        self.assertIn("Synthesizing Context From", tree)

    def test_export_markdown(self):
        graph = load_local_graph("polished-sea-2LmlU")
        md = export_board_markdown(graph)
        self.assertIn("# Poppy AI Board: polished-sea-2LmlU", md)
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
        self.assertEqual(len(payload["nodes"]), 26)
        self.assertEqual(len(payload["edges"]), 5)

    def test_reviews_summary(self):
        summary = get_reviews_summary()
        self.assertEqual(summary["total_reviews"], 161)
        self.assertAlmostEqual(summary["average_tacos"], 4.83, places=1)
        self.assertEqual(summary["distribution"][5], 153)
        self.assertEqual(summary["distribution"][1], 5)

    def test_filter_reviews(self):
        reviews = filter_reviews(limit=3, min_rating=5)
        self.assertLessEqual(len(reviews), 3)
        for r in reviews:
            self.assertEqual(r["rating"], 5)

    def test_filter_questions(self):
        questions = filter_questions(limit=3)
        self.assertLessEqual(len(questions), 3)

    def test_diagnostics_pass(self):
        diag = run_diagnostics()
        self.assertEqual(diag["overall_status"], "PASS")
        check_names = {c["name"] for c in diag["checks"]}
        self.assertIn("Python Runtime", check_names)
        self.assertIn("E2E Visual Screenshots Audit", check_names)
        self.assertIn("Local Board Graph Cache", check_names)
        self.assertIn("AppSumo Intelligence Archive", check_names)
        self.assertIn("Google Firestore Gateway", check_names)
        self.assertIn("Poppy AI Web Edge", check_names)

if __name__ == "__main__":
    unittest.main()
