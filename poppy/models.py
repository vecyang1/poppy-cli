"""Data models for Poppy AI boards, canvas nodes, and AppSumo intelligence."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class BoardMetadata:
    id: str
    name: str
    user_id: str
    owner_name: str
    owner_email: str
    created_at: Optional[datetime] = None
    last_opened_at: Optional[str] = None
    is_starred: bool = False
    folder_id: Optional[str] = None
    is_synced_liveblocks: bool = True
    node_count: int = 0
    edge_count: int = 0

@dataclass
class CanvasNode:
    id: str
    type: str  # groupNode, annotationNode, chatNode, documentNode, textNode, youtubeNode, webScrapperNode
    title: str
    x: float
    y: float
    width: float
    height: float
    data: Dict[str, Any] = field(default_factory=dict)
    parent_group_id: Optional[str] = None

@dataclass
class CanvasEdge:
    id: str
    source_id: str
    target_id: str
    source_handle: str
    target_handle: str
    edge_type: str = "connectionEdge"
    animated: bool = True

@dataclass
class BoardGraph:
    board_id: str
    graph_id: str
    nodes: List[CanvasNode] = field(default_factory=list)
    edges: List[CanvasEdge] = field(default_factory=list)
    raw_content: Optional[str] = None

@dataclass
class AppSumoReview:
    review_id: str
    user_name: str
    rating: int  # 1-5 tacos
    title: str
    content: str
    created_at: str
    is_helpful_count: int = 0
    tier_bought: Optional[str] = None

@dataclass
class AppSumoQuestion:
    question_id: str
    user_name: str
    question_text: str
    created_at: str
    answers: List[Dict[str, Any]] = field(default_factory=list)
