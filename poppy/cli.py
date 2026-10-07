"""Main CLI interface for poppy."""

import sys
import json
import argparse
from typing import Optional
from .boards import list_boards, load_local_graph, render_board_tree, export_board_markdown
from .reviews import get_reviews_summary, filter_reviews, filter_questions, load_deal_data
from .diagnose import run_diagnostics, render_diagnostics_report

def main():
    parser = argparse.ArgumentParser(
        prog="poppy",
        description="Poppy AI Automation & Community Intelligence CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. Boards
    boards_parser = subparsers.add_parser("boards", help="Manage and inspect Poppy boards")
    boards_sub = boards_parser.add_subparsers(dest="subcommand", help="Boards commands")
    
    # boards list
    blist = boards_sub.add_parser("list", help="List user boards")
    blist.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # boards get
    bget = boards_sub.add_parser("get", help="Get board node graph and connections")
    bget.add_argument("board_id", help="Board ID (e.g. polished-sea-2LmlU)")
    bget.add_argument("--format", choices=["tree", "json", "summary"], default="tree", help="Output format")

    # boards export
    bexp = boards_sub.add_parser("export", help="Export board to markdown or JSON")
    bexp.add_argument("board_id", help="Board ID")
    bexp.add_argument("--format", choices=["md", "json"], default="md", help="Export format")
    bexp.add_argument("-o", "--output", help="Output file path (default: stdout)")

    # 2. Reviews
    rev_parser = subparsers.add_parser("reviews", help="Query AppSumo community reviews")
    rev_sub = rev_parser.add_subparsers(dest="subcommand", help="Reviews commands")
    
    # reviews summary
    rsum = rev_sub.add_parser("summary", help="Show AppSumo review intelligence summary")
    rsum.add_argument("--json", action="store_true", help="Output raw JSON")

    # reviews list
    rlist = rev_sub.add_parser("list", help="List filtered reviews")
    rlist.add_argument("--limit", type=int, default=5, help="Max reviews to return")
    rlist.add_argument("--min-rating", type=int, default=1, help="Minimum tacos rating (1-5)")
    rlist.add_argument("--search", help="Search keyword")
    rlist.add_argument("--json", action="store_true", help="Output raw JSON")

    # 3. Questions
    q_parser = subparsers.add_parser("questions", help="Query AppSumo questions & founder answers")
    q_sub = q_parser.add_subparsers(dest="subcommand", help="Questions commands")
    qlist = q_sub.add_parser("list", help="List questions and founder replies")
    qlist.add_argument("--limit", type=int, default=5, help="Max questions to return")
    qlist.add_argument("--search", help="Search keyword")
    qlist.add_argument("--json", action="store_true", help="Output raw JSON")

    # 4. Tiers
    subparsers.add_parser("tiers", help="Display AppSumo 6-tier pricing & features matrix")

    # 5. Diagnose
    diag_parser = subparsers.add_parser("diagnose", help="Run comprehensive diagnostic reconciliation audit")
    diag_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Dispatch
    if args.command == "boards":
        if args.subcommand == "list":
            boards = list_boards()
            if args.json:
                print(json.dumps([b.__dict__ for b in boards], default=str, indent=2))
            else:
                print(f"{'BOARD ID':<24} {'NAME':<20} {'NODES':<8} {'EDGES':<8} {'LAST OPENED':<15} {'OWNER':<15}")
                print("-" * 95)
                for b in boards:
                    print(f"{b.id:<24} {b.name:<20} {b.node_count:<8} {b.edge_count:<8} {b.last_opened_at or 'unknown':<15} {b.owner_name:<15}")
        elif args.subcommand == "get":
            graph = load_local_graph(args.board_id)
            if not graph:
                print(f"Error: Board graph for '{args.board_id}' not found in local cache.", file=sys.stderr)
                sys.exit(1)
            if args.format == "json":
                print(json.dumps({
                    "board_id": graph.board_id,
                    "graph_id": graph.graph_id,
                    "nodes": [n.__dict__ for n in graph.nodes],
                    "edges": [e.__dict__ for e in graph.edges]
                }, indent=2))
            elif args.format == "summary":
                print(f"Board: {graph.board_id} | Graph: {graph.graph_id} | Nodes: {len(graph.nodes)} | Edges: {len(graph.edges)}")
            else:
                print(render_board_tree(graph))
        elif args.subcommand == "export":
            graph = load_local_graph(args.board_id)
            if not graph:
                print(f"Error: Board graph for '{args.board_id}' not found.", file=sys.stderr)
                sys.exit(1)
            content = json.dumps([n.__dict__ for n in graph.nodes], indent=2) if args.format == "json" else export_board_markdown(graph)
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Exported board '{args.board_id}' to {args.output}")
            else:
                print(content)
        else:
            boards_parser.print_help()

    elif args.command == "reviews":
        if args.subcommand == "summary":
            summary = get_reviews_summary()
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print("==================================================")
                print("      APPSUMO COMMUNITY REVIEW INTELLIGENCE       ")
                print("==================================================")
                print(f"Product:         Poppy AI ({summary['deal_slug']})")
                print(f"Total Reviews:   {summary['total_reviews']}")
                print(f"Average Rating:  ⭐ {summary['average_tacos']} / 5 Tacos")
                print(f"Distribution:    5★: {summary['distribution'][5]} | 4★: {summary['distribution'][4]} | 3★: {summary['distribution'][3]} | 2★: {summary['distribution'][2]} | 1★: {summary['distribution'][1]}")
                print(f"Sentiment Ratio: {summary['positive_mentions']} Positive vs {summary['critique_mentions']} Critiques")
                print("\n🌟 Top Strengths Identified:")
                for p in summary["key_positives"]:
                    print(f"  • {p}")
                print("\n⚠️  Top Customer Friction Points:")
                for f in summary["key_friction_points"]:
                    print(f"  • {f}")
                print("==================================================")
        elif args.subcommand == "list":
            reviews = filter_reviews(limit=args.limit, min_rating=args.min_rating, search=args.search)
            if args.json:
                print(json.dumps(reviews, indent=2))
            else:
                print(f"Found {len(reviews)} reviews (limit: {args.limit}):\n")
                for r in reviews:
                    print(f"[{'⭐' * r['rating']}] {r['title']} - by {r['name']} ({r['date']})")
                    print(f"  {r['content']}")
                    print("-" * 60)
        else:
            rev_parser.print_help()

    elif args.command == "questions":
        if args.subcommand == "list":
            questions = filter_questions(limit=args.limit, search=args.search)
            if args.json:
                print(json.dumps(questions, indent=2))
            else:
                print(f"Found {len(questions)} Q&A threads (limit: {args.limit}):\n")
                for q in questions:
                    print(f"❓ {q['author']}: {q['question']}")
                    print(f"   💬 Founder: {q['founder_reply']}")
                    print("-" * 60)
        else:
            q_parser.print_help()

    elif args.command == "tiers":
        deal = load_deal_data()
        tiers = deal.get("plans") or []
        print("==========================================================================================")
        print("                         APPSUMO POPPY AI PRICING & TIER MATRIX                           ")
        print("==========================================================================================")
        print(f"{'TIER':<10} {'PRICE':<10} {'CREDITS':<15} {'BRANDS':<12} {'SEATS':<8} {'KEY PERKS':<25}")
        print("-" * 90)
        for t in tiers:
            name = t.get("name", "Tier")
            price = f"${t.get('price', 0)}"
            credits = f"{t.get('credits_per_month', 'N/A')}/mo"
            brands = str(t.get("brands_limit", "N/A"))
            seats = str(t.get("seats_limit", "1"))
            perks = []
            if t.get("has_byok"): perks.append("BYOK")
            if t.get("has_api"): perks.append("API")
            if t.get("has_chatbot"): perks.append("Chatbot")
            perk_str = ", ".join(perks) if perks else "Standard Features"
            print(f"{name:<10} {price:<10} {credits:<15} {brands:<12} {seats:<8} {perk_str:<25}")
        print("==========================================================================================")

    elif args.command == "diagnose":
        diag = run_diagnostics()
        if args.json:
            print(json.dumps(diag, indent=2))
        else:
            print(render_diagnostics_report(diag))
