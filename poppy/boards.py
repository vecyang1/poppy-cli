"""Board operations, React Flow graph parsing, tree visualization, and export utilities."""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from .models import BoardMetadata, CanvasNode, CanvasEdge, BoardGraph

DEFAULT_BOARDS_SNAPSHOT = [
    {
        "id": "polished-sea-2LmlU",
        "name": "Ivory Antelope",
        "userId": "86f5b982-23fa-452a-9017-f246391688b4",
        "owner": {
            "name": "Alex Vy",
            "email": "alex@example.com"
        },
        "dateCreated": {"seconds": 1791375115},
        "lastOpened": "1 hour ago",
        "starred": False,
        "isSyncedToLiveblocks": True,
        "graphId": "BNW7aGRhauOFL1L5SKFi"
    },
    {
        "id": "late-pine-VaMMW",
        "name": "Blush Bonobo",
        "userId": "86f5b982-23fa-452a-9017-f246391688b4",
        "owner": {
            "name": "Alex Vy",
            "email": "alex@example.com"
        },
        "dateCreated": {"seconds": 1787648434},
        "lastOpened": "1 month ago",
        "starred": False,
        "isSyncedToLiveblocks": True,
        "graphId": None
    }
]

def get_base_dir() -> Path:
    # Resolves to project root
    return Path(__file__).resolve().parent.parent

def _parse_board_graph_data(board_id: str, data: Dict[str, Any]) -> BoardGraph:
    nodes = []
    for n in data.get("nodes", []):
        pos = n.get("position", {})
        meas = n.get("measured", {})
        nodes.append(CanvasNode(
            id=n.get("id", ""),
            type=n.get("type", "unknown"),
            title=n.get("title") or n.get("data", {}).get("title") or n.get("id", ""),
            x=pos.get("x", 0.0),
            y=pos.get("y", 0.0),
            width=meas.get("width") or n.get("width", 0.0),
            height=meas.get("height") or n.get("height", 0.0),
            data=n.get("data", {})
        ))
    edges = []
    for e in data.get("edges", []):
        edges.append(CanvasEdge(
            id=e.get("id", ""),
            source_id=e.get("source", ""),
            target_id=e.get("target", ""),
            source_handle=e.get("sourceHandle", ""),
            target_handle=e.get("targetHandle", ""),
            edge_type=e.get("type", "connectionEdge"),
            animated=e.get("animated", True)
        ))
    graph_id = data.get("graphId")
    if not graph_id:
        for n_raw in data.get("nodes", []):
            if n_raw.get("graphId"):
                graph_id = n_raw.get("graphId")
                break
            if n_raw.get("data", {}).get("graphId"):
                graph_id = n_raw["data"]["graphId"]
                break
    if not graph_id:
        for b in DEFAULT_BOARDS_SNAPSHOT:
            if b.get("id") == board_id and b.get("graphId"):
                graph_id = b["graphId"]
                break
    graph_id = graph_id or "unknown"

    return BoardGraph(
        board_id=board_id,
        graph_id=graph_id,
        nodes=nodes,
        edges=edges
    )

def load_local_graph(board_id: str) -> Optional[BoardGraph]:
    base_dir = get_base_dir()
    candidate_paths = [
        base_dir / f"board_{board_id}.json",
        base_dir / f"board_{board_id.replace('-', '_')}.json",
        base_dir / f"board_{board_id.replace('_', '-')}.json",
        base_dir / "board_polished_sea_2LmlU.json" if board_id in ("polished-sea-2LmlU", "default") else None
    ]
    for p in candidate_paths:
        if p and p.exists():
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            return _parse_board_graph_data(board_id, data)

    # Fallback search across any board_*.json files in base_dir
    for p in base_dir.glob("board_*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            found_bid = data.get("boardId") or data.get("id")
            if not found_bid:
                for n in data.get("nodes", []):
                    if n.get("boardId"):
                        found_bid = n["boardId"]
                        break
            norm_target = board_id.replace("-", "_")
            stem = p.stem
            file_bid = (stem[6:] if stem.startswith("board_") else stem).replace("-", "_")
            if (found_bid and found_bid.replace("-", "_") == norm_target) or file_bid == norm_target:
                return _parse_board_graph_data(board_id, data)
        except Exception:
            continue
    return None

def list_boards() -> List[BoardMetadata]:
    boards = []
    base_dir = get_base_dir()
    seen_ids = set()

    # 1. Start with default snapshot boards
    for item in DEFAULT_BOARDS_SNAPSHOT:
        bid = item["id"]
        seen_ids.add(bid)
        seen_ids.add(bid.replace("-", "_"))
        seen_ids.add(bid.replace("_", "-"))
        # Check node count if local graph exists
        graph = load_local_graph(bid)
        node_count = len(graph.nodes) if graph else 0
        edge_count = len(graph.edges) if graph else 0
        
        boards.append(BoardMetadata(
            id=bid,
            name=item["name"],
            user_id=item["userId"],
            owner_name=item["owner"]["name"],
            owner_email=item["owner"]["email"],
            last_opened_at=item["lastOpened"],
            is_starred=item["starred"],
            is_synced_liveblocks=item["isSyncedToLiveblocks"],
            node_count=node_count,
            edge_count=edge_count
        ))

    # 2. Dynamically discover any board_*.json files in base_dir
    for p in sorted(base_dir.glob("board_*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        bid = data.get("boardId") or data.get("id")
        if not bid:
            for n in nodes:
                if n.get("boardId"):
                    bid = n["boardId"]
                    break
        if not bid:
            stem = p.stem
            bid = stem[6:] if stem.startswith("board_") else stem

        if bid in seen_ids or bid.replace("-", "_") in seen_ids or bid.replace("_", "-") in seen_ids:
            continue

        seen_ids.add(bid)
        seen_ids.add(bid.replace("-", "_"))
        seen_ids.add(bid.replace("_", "-"))

        name = data.get("name") or data.get("title")
        if not name:
            for n in nodes:
                if n.get("title"):
                    name = n["title"]
                    break
                if n.get("data", {}).get("title"):
                    name = n["data"]["title"]
                    break
        if not name:
            name = bid.replace("_", " ").replace("-", " ").title()

        user_id = data.get("userId") or "local-user"
        owner_name = data.get("owner", {}).get("name") or "Local User"
        owner_email = data.get("owner", {}).get("email") or "user@example.com"
        for n in nodes:
            ndata = n.get("data", {})
            if ndata.get("userName"):
                owner_name = ndata["userName"]
            if ndata.get("userEmail"):
                owner_email = ndata["userEmail"]
            if n.get("userId"):
                user_id = n["userId"]
            if owner_name != "Local User":
                break

        boards.append(BoardMetadata(
            id=bid,
            name=name,
            user_id=user_id,
            owner_name=owner_name,
            owner_email=owner_email,
            last_opened_at="local cache",
            is_starred=bool(data.get("starred", False)),
            is_synced_liveblocks=bool(data.get("isSyncedToLiveblocks", False)),
            node_count=len(nodes),
            edge_count=len(edges)
        ))
    return boards

def render_board_tree(graph: BoardGraph) -> str:
    lines = []
    lines.append(f"📦 Board: {graph.board_id} (Graph ID: {graph.graph_id})")
    lines.append(f"   Total Nodes: {len(graph.nodes)} | Edges: {len(graph.edges)}")
    lines.append("")
    
    # Categorize nodes
    groups = [n for n in graph.nodes if n.type == "groupNode"]
    chats = [n for n in graph.nodes if n.type == "chatNode"]
    others = [n for n in graph.nodes if n.type not in ("groupNode", "chatNode")]
    
    lines.append("🏷️  Functional Groups:")
    for g in groups:
        lines.append(f"   ├─ [{g.type}] {g.title} (ID: {g.id}) @ ({int(g.x)}, {int(g.y)}) [{int(g.width)}x{int(g.height)}]")
    
    lines.append("\n🤖 AI Chat Hubs:")
    for c in chats:
        lines.append(f"   ├─ [{c.type}] {c.title} (ID: {c.id})")
        # Find incoming edges
        incoming = [e for e in graph.edges if e.target_id == c.id]
        if incoming:
            lines.append("      🔗 Synthesizing Context From:")
            for inc in incoming:
                src_node = next((n for n in graph.nodes if n.id == inc.source_id), None)
                src_title = src_node.title if src_node else inc.source_id
                lines.append(f"         └── {src_title} ({inc.source_handle} -> {inc.target_handle})")

    lines.append("\n📄 Content & Ingestion Nodes:")
    for o in others:
        lines.append(f"   ├─ [{o.type}] {o.title} (ID: {o.id})")

    return "\n".join(lines)

def export_board_markdown(graph: BoardGraph) -> str:
    md = []
    md.append(f"# Poppy AI Board: {graph.board_id}\n")
    md.append(f"> **Graph ID**: `{graph.graph_id}`  ")
    md.append(f"> **Node Count**: {len(graph.nodes)}  ")
    md.append(f"> **Edge Count**: {len(graph.edges)}  \n")
    
    md.append("## Canvas Nodes\n")
    for n in graph.nodes:
        md.append(f"### {n.title} (`{n.type}`)")
        md.append(f"- **ID**: `{n.id}`")
        md.append(f"- **Position**: x={n.x}, y={n.y}")
        md.append(f"- **Dimensions**: {n.width} x {n.height}")
        if n.data:
            summary = n.data.get("title") or n.data.get("userName") or ""
            if summary:
                md.append(f"- **Metadata**: {summary}")
        md.append("")

    md.append("## Connections & Data Flow\n")
    for e in graph.edges:
        md.append(f"- `{e.source_id}` (`{e.source_handle}`) ──▶ `{e.target_id}` (`{e.target_handle}`)")

    return "\n".join(md)
