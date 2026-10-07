"""AppSumo review intelligence, Q&A queries, and sentiment analysis."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

def get_appsumo_dir() -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / "appsumo"

def load_reviews_data() -> List[Dict[str, Any]]:
    p = get_appsumo_dir() / "reviews.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_questions_data() -> List[Dict[str, Any]]:
    p = get_appsumo_dir() / "questions.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_deal_data() -> Dict[str, Any]:
    p = get_appsumo_dir() / "deal.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_reviews_summary() -> Dict[str, Any]:
    reviews = load_reviews_data()
    total = len(reviews)
    ratings_dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        score = int(r.get("rating", 5))
        if score in ratings_dist:
            ratings_dist[score] += 1
            
    avg_rating = sum(k * v for k, v in ratings_dist.items()) / total if total > 0 else 0.0

    # Common praise and complaints extraction
    positive_keywords = ["intuitive", "speed", "canvas", "repurpose", "workflow", "youtube", "voice"]
    critique_keywords = ["price", "expensive", "credit", "bug", "lag", "crash", "support", "refund"]
    
    pos_mentions = 0
    neg_mentions = 0
    for r in reviews:
        text = (r.get("review") or r.get("title") or "").lower()
        if any(w in text for w in positive_keywords):
            pos_mentions += 1
        if any(w in text for w in critique_keywords):
            neg_mentions += 1

    return {
        "deal_slug": "poppy-ai",
        "total_reviews": total,
        "average_tacos": round(avg_rating, 2),
        "distribution": ratings_dist,
        "positive_mentions": pos_mentions,
        "critique_mentions": neg_mentions,
        "key_positives": [
            "Visual canvas workflow eliminates Google Docs <-> ChatGPT tab-switching fatigue",
            "Multi-source ingestion (YouTube videos, PDFs, Instagram Reels, voice notes) in one board",
            "Non-linear branching allows connecting multiple research cards directly into AI chat"
        ],
        "key_friction_points": [
            "High entry price point ($279 Tier 1 to $4,459 Tier 6)",
            "Credit burn rate on heavy LLM reasoning and video transcripts",
            "BYOK (Bring Your Own Key) locked behind Tier 4+ ($1,379+)"
        ]
    }

def filter_reviews(limit: int = 10, min_rating: int = 1, search: Optional[str] = None) -> List[Dict[str, Any]]:
    reviews = load_reviews_data()
    filtered = []
    search_lower = search.lower() if search else None
    
    for r in reviews:
        rating = int(r.get("rating", 5))
        if rating < min_rating:
            continue
        text = f"{r.get('title', '')} {r.get('review', '')}"
        if search_lower and search_lower not in text.lower():
            continue
        filtered.append({
            "name": r.get("author") or r.get("user", {}).get("name") or "Anonymous",
            "rating": rating,
            "title": r.get("title") or "No title",
            "date": r.get("created_at") or r.get("date") or "",
            "content": (r.get("review") or "")[:200] + ("..." if len(r.get("review", "")) > 200 else "")
        })
        if len(filtered) >= limit:
            break
            
    return filtered

def filter_questions(limit: int = 10, search: Optional[str] = None) -> List[Dict[str, Any]]:
    questions = load_questions_data()
    filtered = []
    search_lower = search.lower() if search else None
    
    for q in questions:
        text = f"{q.get('question', '')} {q.get('title', '')}"
        if search_lower and search_lower not in text.lower():
            continue
        answers = q.get("answers") or []
        first_answer = answers[0] if answers else {}
        filtered.append({
            "id": q.get("id"),
            "author": q.get("author") or q.get("user", {}).get("name") or "Sumoling",
            "question": (q.get("question") or "")[:150] + ("..." if len(q.get("question", "")) > 150 else ""),
            "answer_count": len(answers),
            "founder_reply": (first_answer.get("answer") or "")[:150] + ("..." if len(first_answer.get("answer", "")) > 150 else "") if first_answer else "No reply"
        })
        if len(filtered) >= limit:
            break
            
    return filtered
