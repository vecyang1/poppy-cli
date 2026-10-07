# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-07

### Added
- **Dynamic Board Discovery (`poppy/boards.py`)**: Automatically scans and indexes local `board_*.json` canvas files from project root alongside default snapshots with deduplication.
- **Structural JWT Validation (`poppy/diagnose.py`)**: Standard-library 3-part base64url JWT header/payload structural validation (`validate_jwt_structure`) with algorithm and subject extraction.
- **Dynamic Diagnostics Status Banner & Failure Propagation (`poppy/diagnose.py`)**: Replaced static status string with dynamic status computation across Firestore, Clerk, Firebase, and AppSumo checks; failure states in network gateways or malformed tokens properly propagate to `overall_status = "FAIL"`.
- **Adversarial Test Suite Hardening (`tests/test_cli.py`)**: Expanded test suite to 17 tests covering boundary zero limits, network outage simulations, malformed token rejections, unconfigured warnings, and dynamic board discovery.

### Fixed
- **Review & Question Filter Boundary Defect (`poppy/reviews.py`)**: Fixed off-by-one error where `--limit 0` returned 1 item; added immediate short-circuit returning `[]` for `limit <= 0`.
- **Honest Diagnostic Authentication Reporting (`poppy/diagnose.py`)**: Diagnostic check reports honest `WARN` with `"Unconfigured"` status when authentication tokens are not set, rather than falsely self-certifying `"valid"`.

## [1.1.0] - 2026-10-07

### Added
- **AppSumo Tiers Parser & JSON Output**: `poppy tiers` now parses `plan_features` from `deal.json` and supports `--json` programmatic export for all 6 tiers ($279 - $4,459).
- **Deep Test Suite Coverage**: Enhanced test suite to 10 comprehensive tests with deep assertions on extracted review comments, author usernames, founder replies, tier perks, board `graphId`, and E2E CLI command execution.

### Fixed
- **Reviews & Questions Schema Mappings**:
  - `poppy reviews list` now maps `user.username`, `created`, and `comment` to display actual authors, dates, and review content.
  - `poppy questions list` now maps `user.username`, `created`, `comment`, and thread `children` to display actual questions and founder replies.
  - `poppy reviews summary` scans both `title` and `comment` for sentiment keywords, correctly calculating 67 positive vs 74 critique mentions.
- **Board Graph ID Resolution**: `poppy boards get` and `export` now resolve `graphId` (`BNW7aGRhauOFL1L5SKFi`) from node root, data, or snapshot, replacing `"unknown"`.
- **Board JSON Export**: `poppy boards export --format json` now includes both `nodes` and `edges` arrays along with graph metadata.
- **Diagnostic Engine Hardening**:
  - Increased screenshot validation threshold to `> 100_000` bytes so blank loading screens fail validation.
  - Added explicit checks for Clerk Authentication, Firebase Auth Token, Google Firestore 200, and AppSumo ledger caching.
  - Added real formatted UTC ISO timestamp (`timestamp: YYYY-MM-DDTHH:MM:SSZ`).
- **Visual Evidence Remediation**: Replaced incomplete and mislabeled screenshots so all 7 files in `screenshots/` are genuine, high-res (>100KB), non-blank, viewport-only captures representing each functional surface (`01_boards_dashboard.png` through `07_upgrades_pricing.png`).

### Security
- **Privacy Hygiene**: Purged legacy raw screenshots containing browser tabs/bookmarks (`screenshots/legacy/`) from Git tracking.
- **Git Exclusions**: Added `.gitignore` patterns for `Google Chrome *.png`, `Path Finder *.png`, and `screenshots/legacy/`.

## [1.0.0] - 2026-10-07

### Added
- **E2E Visual Evidence Suite**: Full-resolution programmatic screenshot capture for 7 core workspace surfaces (`01_boards_dashboard.png` to `07_upgrades_pricing.png`).
- **Reverse-Engineered Architecture Mapping**: Detailed mapping of Google Cloud Firestore database (`poppy-ai-16252`), Clerk authentication token lifecycle, and Liveblocks real-time layer.
- **Board Graph Parser & ASCII Visualizer**: `poppy boards get <id>` rendering functional groups, connected context nodes, and AI chat hubs.
- **Markdown & JSON Export**: `poppy boards export <id>` allowing structured note extraction.
- **AppSumo Intelligence Archive**: Complete scrape of 161 reviews, 184 questions, 10 FAQs, and 6 licensing tiers ($279 - $4,459).
- **Diagnostic Reconciliation Engine**: `poppy diagnose` subcommand providing 6-point verification covering screenshots, cache, and cloud gateways.
- **Automated Test Suite**: 7 unit and integration tests passing with 100% OK.
- **Global CLI Exposure**: Linked to `~/.local/bin/poppy` and verified from `$HOME`.

### Security
- Sanitized machine paths, personal emails, and auth tokens to prevent credential leaks.
- Zero secrets committed in public code paths.
