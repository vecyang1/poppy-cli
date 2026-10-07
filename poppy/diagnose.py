"""Diagnostic reconciliation engine for Poppy AI environment, assets, and connectivity."""

import sys
import os
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, List

def run_diagnostics() -> Dict[str, Any]:
    base_dir = Path(__file__).resolve().parent.parent
    results = {
        "timestamp": None,
        "checks": [],
        "overall_status": "PASS"
    }

    # 1. Environment Check
    results["checks"].append({
        "name": "Python Runtime",
        "status": "PASS",
        "details": f"Python {sys.version.split()[0]} on {sys.platform}"
    })

    # 2. Local Screenshots Evidence Suite
    screenshots_dir = base_dir / "screenshots"
    expected_shots = [
        "01_boards_dashboard.png",
        "02_canvas_board.png",
        "03_vault_assets.png",
        "04_templates.png",
        "05_brands.png",
        "06_referral_rewards.png",
        "07_upgrades_pricing.png"
    ]
    missing_shots = []
    found_shots = 0
    if screenshots_dir.exists():
        for s in expected_shots:
            p = screenshots_dir / s
            if p.exists() and p.stat().st_size > 1000:
                found_shots += 1
            else:
                missing_shots.append(s)
    else:
        missing_shots = expected_shots

    if not missing_shots:
        results["checks"].append({
            "name": "E2E Visual Screenshots Audit",
            "status": "PASS",
            "details": f"All {found_shots}/{len(expected_shots)} full-resolution PNG screenshots verified"
        })
    else:
        results["overall_status"] = "WARN"
        results["checks"].append({
            "name": "E2E Visual Screenshots Audit",
            "status": "WARN",
            "details": f"Found {found_shots}/{len(expected_shots)}. Missing/small: {missing_shots}"
        })

    # 3. Graph Cache Integrity
    graph_path = base_dir / "board_polished_sea_2LmlU.json"
    if graph_path.exists():
        try:
            with open(graph_path, "r", encoding="utf-8") as f:
                gdata = json.load(f)
            node_cnt = len(gdata.get("nodes", []))
            edge_cnt = len(gdata.get("edges", []))
            results["checks"].append({
                "name": "Local Board Graph Cache",
                "status": "PASS",
                "details": f"Graph verified: {node_cnt} nodes, {edge_cnt} connection edges"
            })
        except Exception as e:
            results["overall_status"] = "FAIL"
            results["checks"].append({
                "name": "Local Board Graph Cache",
                "status": "FAIL",
                "details": f"Corrupt JSON: {e}"
            })
    else:
        results["overall_status"] = "WARN"
        results["checks"].append({
            "name": "Local Board Graph Cache",
            "status": "WARN",
            "details": "board_polished_sea_2LmlU.json missing"
        })

    # 4. AppSumo Community Dataset Audit
    appsumo_dir = base_dir / "data" / "appsumo"
    req_files = ["reviews.json", "questions.json", "faqs.json", "deal.json", "DOSSIER.md"]
    appsumo_ok = True
    counts = {}
    for rf in req_files:
        fp = appsumo_dir / rf
        if not fp.exists() or fp.stat().st_size == 0:
            appsumo_ok = False
            break
        if rf.endswith(".json"):
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                counts[rf] = len(cdata) if isinstance(cdata, list) else "valid"
            except Exception:
                appsumo_ok = False
    
    if appsumo_ok:
        results["checks"].append({
            "name": "AppSumo Intelligence Archive",
            "status": "PASS",
            "details": f"Cached 100%: {counts.get('reviews.json', 0)} reviews, {counts.get('questions.json', 0)} questions, {counts.get('faqs.json', 0)} FAQs"
        })
    else:
        results["overall_status"] = "WARN"
        results["checks"].append({
            "name": "AppSumo Intelligence Archive",
            "status": "WARN",
            "details": "Incomplete AppSumo dataset"
        })

    # 5. Remote Connectivity
    def check_url(url: str, timeout: int = 5) -> bool:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Poppy-CLI-Doctor/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status < 500
        except urllib.error.HTTPError as e:
            # 400, 401, 403, 404 prove host resolution and TLS handshake succeeded
            return e.code < 500
        except Exception:
            return False

    fs_ok = check_url("https://firestore.googleapis.com/")
    results["checks"].append({
        "name": "Google Firestore Gateway",
        "status": "PASS" if fs_ok else "FAIL",
        "details": "Connected (firestore.googleapis.com)" if fs_ok else "Unreachable"
    })

    poppy_ok = check_url("https://app.getpoppy.ai/")
    results["checks"].append({
        "name": "Poppy AI Web Edge",
        "status": "PASS" if poppy_ok else "FAIL",
        "details": "Connected (app.getpoppy.ai)" if poppy_ok else "Unreachable"
    })

    return results

def render_diagnostics_report(diag: Dict[str, Any]) -> str:
    lines = []
    lines.append("==================================================")
    lines.append("        POPPY AI DIAGNOSTIC AUDIT REPORT          ")
    lines.append("==================================================")
    for c in diag["checks"]:
        badge = "✓" if c["status"] == "PASS" else ("⚠" if c["status"] == "WARN" else "✗")
        lines.append(f"  [{badge}] {c['name']:<30} : {c['details']}")
    lines.append("--------------------------------------------------")
    lines.append(f"Overall Status: {diag['overall_status']}")
    lines.append("==================================================")
    return "\n".join(lines)
