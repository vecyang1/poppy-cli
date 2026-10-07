# Project: Poppy AI Programmatic CLI, Deep E2E Probe Suite & AppSumo Review Ledger

## Architecture
- **CLI Subsystem (`poppy/`)**: Python CLI following OpenCLI specification, Click interface, structured tables and JSON output.
- **Data & Canvas Subsystem**: React Flow infinite canvas graph parser (`graphs/{graphId}`), 7 node types, edge connector mappings.
- **Intelligence Ledger Subsystem (`data/appsumo/`)**: 161 reviews, 184 Q&As, 10 FAQs, 8 updates, 6 pricing tiers, synthesis dossier.
- **Visual Evidence Subsystem (`screenshots/`)**: 7 high-res PNG functional surface captures.
- **Verification & Hygiene Subsystem**: Unit/E2E test suite, github-ops sanitization, backward-compatible symlinks.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Board Listing (`poppy boards list`) | List boards with owner, dates, node counts | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Board Graph Rendering (`poppy boards get`) | Display node hierarchy & edges with proper graphId | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Board Export (`poppy boards export`) | Export board nodes and edges in JSON or MD | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Diagnostic Check (`poppy diagnose`) | Verify Clerk/Firebase auth, Firestore 200, cache | M1 | ORIGINAL_REQUEST §R1 |
| 5 | AppSumo Reviews Summary (`poppy reviews summary`) | Sentiment ratio, tacos average, ratings distribution | M1 | ORIGINAL_REQUEST §R1 |
| 6 | AppSumo Reviews List (`poppy reviews list`) | Schema mapping for comments, usernames, dates | M1 | ORIGINAL_REQUEST §R3 |
| 7 | AppSumo Questions (`poppy questions list`) | Schema mapping for questions and replies | M1 | ORIGINAL_REQUEST §R3 |
| 8 | AppSumo Tiers (`poppy tiers`) | Schema mapping for 6 pricing tiers and features | M1 | ORIGINAL_REQUEST §R3 |
| 9 | Global CLI PATH Exposure | `~/.local/bin/poppy` runnable from `$HOME` | M1 | ORIGINAL_REQUEST §R1 |
| 10 | Clean 7 High-Res Screenshots | Viewport captures without browser chrome/personal tabs | M2 | ORIGINAL_REQUEST §R2 |
| 11 | Privacy & Git Hygiene | Untrack raw screenshots, update .gitignore | M2 | ORIGINAL_REQUEST §R4 |
| 12 | AppSumo Ledger & Dossier | Archive completeness & strengths/weaknesses synthesis | M3 | ORIGINAL_REQUEST §R3 |
| 13 | Documentation & Symlink | API.md, CHANGELOG.md, README.md, GetPoppy symlink | M3 | ORIGINAL_REQUEST §R4 |
| 14 | Deep Test Suite Hardening | Comprehensive unit & E2E tests for all CLI flows | M4 | ORIGINAL_REQUEST §AC |
| 15 | Forensic Integrity & Gating | Verify 100% genuine code, zero secrets, zero cheating | M4 | ORIGINAL_REQUEST §R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | CLI Core & Schema Remediation | Fix schema bugs, board export edges, graphId, diagnose auth checks | Survey | IN_PROGRESS |
| M2 | Visual Evidence & Privacy Hygiene | Fix 7 screenshots (viewport-only), untrack raw chrome images, update .gitignore | Survey | PLANNED |
| M3 | Intelligence Ledger & Documentation | Verify dossier synthesis, update CHANGELOG.md, API.md, README.md | M1, M2 | PLANNED |
| M4 | Comprehensive Testing & Integrity Gate | Deep tests, Reviewers, Challengers, and Forensic Audit | M1, M2, M3 | PLANNED |

## Interface Contracts
### CLI Entrypoint
- Executable: `bin/poppy` symlinked to `~/.local/bin/poppy`
- Invocation: `poppy <command> [subcommand] [flags]`
- JSON output contract: `--json` flag on commands emits valid JSON to stdout with exit code 0.

### Board Graph Contract
- Nodes: 26 nodes (5 groups, 1 chatNode, 20 content nodes)
- Edges: 5 connectionEdges linking source nodes to chatNode target
- Export JSON format: `{"graphId": str, "nodes": [...], "edges": [...]}`

### AppSumo Schema Contract
- Reviews: `comment`, `user.username`, `created`, `rating` (tacos)
- Questions: `comment`, `user.username`, `created`, `children` (replies)
- Tiers: `plan_features` array containing limits, pricing, and features

## Code Layout
- `bin/poppy`: Executable wrapper
- `poppy/`: Python package
  - `cli.py`: Click CLI entrypoint and command definitions
  - `boards.py`: Board fetch, parse, render, export
  - `reviews.py`: AppSumo dataset loading, aggregation, filtering
  - `diagnose.py`: System health, auth token checks, screenshot size checks
  - `models.py`: Data models and constants
- `data/appsumo/`: Cached reviews, questions, FAQs, founders, deal, dossiers
- `screenshots/`: 7 primary functional surface PNG screenshots
- `tests/`: Test suite
  - `test_cli.py`: Unit and integration test assertions
