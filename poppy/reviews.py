"""AppSumo review intelligence, Q&A queries, and sentiment analysis."""

import re
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
        text = f"{r.get('title') or ''} {r.get('comment') or r.get('review') or ''}".lower()
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
    if limit <= 0:
        return []
    reviews = load_reviews_data()
    filtered = []
    search_lower = search.lower() if search else None
    
    for r in reviews:
        rating = int(r.get("rating", 5))
        if rating < min_rating:
            continue
        comment = r.get("comment") or r.get("review") or ""
        title = r.get("title") or ""
        text = f"{title} {comment}"
        if search_lower and search_lower not in text.lower():
            continue
        user = r.get("user") or {}
        author = user.get("username") or user.get("name") or r.get("author") or "Anonymous"
        date = r.get("created") or r.get("created_at") or r.get("date") or ""
        filtered.append({
            "name": author,
            "rating": rating,
            "title": title or "No title",
            "date": date[:10] if date else "",
            "content": comment[:200] + ("..." if len(comment) > 200 else "")
        })
        if len(filtered) >= limit:
            break
            
    return filtered

def filter_questions(limit: int = 10, search: Optional[str] = None) -> List[Dict[str, Any]]:
    if limit <= 0:
        return []
    questions = load_questions_data()
    filtered = []
    search_lower = search.lower() if search else None
    
    for q in questions:
        q_text = q.get("comment") or q.get("question") or ""
        title = q.get("title") or ""
        text = f"{title} {q_text}"
        if search_lower and search_lower not in text.lower():
            continue
        user = q.get("user") or {}
        author = user.get("username") or user.get("name") or q.get("author") or "Sumoling"
        children = q.get("children") or q.get("answers") or []
        reply_obj = next((c for c in children if c.get("answer_type") in ("partner", "staff")), None)
        if not reply_obj and children:
            reply_obj = children[0]
            
        if reply_obj:
            reply_user = reply_obj.get("user", {}).get("username") or reply_obj.get("author") or "Founder"
            reply_text = reply_obj.get("comment") or reply_obj.get("answer") or ""
            reply_str = f"[{reply_user}]: {reply_text[:150]}..." if reply_text else "No reply"
        else:
            reply_str = "No reply"

        filtered.append({
            "id": q.get("id"),
            "author": author,
            "title": title,
            "question": q_text[:150] + ("..." if len(q_text) > 150 else ""),
            "answer_count": len(children),
            "founder_reply": reply_str
        })
        if len(filtered) >= limit:
            break
            
    return filtered

def get_deal_tiers() -> List[Dict[str, Any]]:
    deal = load_deal_data()
    raw_plans = deal.get("plans") or []
    tiers = []
    for p in raw_plans:
        tier_num = p.get("tier", 1)
        price_val = float(p.get("price", 0))
        price_str = f"${int(price_val):,}" if price_val.is_integer() else f"${price_val:,.2f}"
        features = p.get("plan_features") or []
        feat_texts = []
        for f in features:
            txt = f.get("feature", "") if isinstance(f, dict) else str(f)
            clean = re.sub(r"<[^>]+>", "", txt).strip()
            if clean:
                feat_texts.append(clean)
        
        credits = next((f for f in feat_texts if "Monthly credits" in f), "N/A")
        credits_clean = credits.replace(" Monthly credits", "/mo") if "Monthly credits" in credits else credits
        brands = next((f for f in feat_texts if "Brand" in f), "N/A")
        seats = next((f for f in feat_texts if "Seat" in f), "1 Seat")
        
        perks = []
        for f in feat_texts:
            if "BYOK" in f:
                perks.append("BYOK")
            elif "API" in f:
                perks.append("API")
            elif "White-label" in f or "White-labelled" in f:
                perks.append("White-Label")
            elif "Chatbot" in f:
                perks.append("Chatbots")
        perks_unique = list(dict.fromkeys(perks))
        perk_str = ", ".join(perks_unique) if perks_unique else "Standard Features"
        
        tiers.append({
            "tier": tier_num,
            "name": f"Tier {tier_num}",
            "price": price_str,
            "price_usd": price_val,
            "credits_per_month": credits_clean,
            "brands_limit": brands,
            "seats_limit": seats,
            "key_perks": perk_str,
            "features": feat_texts
        })
    return tiers
