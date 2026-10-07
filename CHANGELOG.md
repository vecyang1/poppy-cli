# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
