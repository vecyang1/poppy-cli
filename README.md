# Poppy AI Automation CLI & Reverse-Engineered Workspace Suite

A production-grade, agent-native CLI, reverse-engineered API specification, and community intelligence archive for [Poppy AI](https://getpoppy.ai) (`app.getpoppy.ai`).

Built with **Zero Ghost Logic**, **Diagnostic-First Architecture**, and **Evidence-Backed Verification**.

---

## 🌟 Overview & Capabilities

Poppy AI is a visual, non-linear AI workspace designed for content creators, agencies, and copywriters. It replaces linear ChatGPT chat threads with a 2D infinite canvas where users can import YouTube videos, documents, web pages, and brand guidelines, connecting them directly into AI chat nodes for structured content synthesis.

### Key Capabilities

- **Infinite Canvas Board Management**: Manage boards, list active projects, inspect node hierarchies, and export canvas graphs to structured Markdown or JSON.
- **Reverse-Engineered Schema Ground Truth**: Direct mapping of React Flow canvas nodes (`groupNode`, `chatNode`, `youtubeNode`, `documentNode`, `annotationNode`, `webScrapperNode`) and directed context edges (`connectionEdge`).
- **AppSumo Community Intelligence**: Complete archive of 161 AppSumo customer reviews (⭐4.83 / 5 tacos), 184 community questions, 10 FAQs, and 6-tier licensing matrices.
- **Diagnostic Reconciliation**: Built-in `poppy diagnose` command verifying local visual evidence, cache integrity, and cloud API connectivity.
- **Global Zero-Friction Availability**: Instantly callable from `$HOME` via `poppy` (`~/.local/bin/poppy`).

---

## 📸 Visual Evidence Suite (E2E Screenshots)

All screenshots were programmatically captured and verified using `ego-browser`:

| Feature Surface | Screenshot | Description |
| :--- | :--- | :--- |
| **Boards Dashboard** | `screenshots/01_boards_dashboard.png` | Workspace overview with folders, boards, and search |
| **Infinite Canvas** | `screenshots/02_canvas_board.png` | Live 26-node React Flow board with connected AI chat hub |
| **Media Vault** | `screenshots/03_vault_assets.png` | Central asset library for docs, videos, and media |
| **Templates Library**| `screenshots/04_templates.png` | Pre-built viral templates (YouTube, Reels, TikTok, FB Ads)|
| **Brands Manager** | `screenshots/05_brands.png` | Brand voices, guidelines, and tone presets |
| **Refer & Earn** | `screenshots/06_referral_rewards.png`| Referral modal ($80 cash / 5,000 credits incentive) |
| **Upgrades & Tiers** | `screenshots/07_upgrades_pricing.png` | Plan matrix and credit top-up modal |

---

## 🚀 Quick Start & CLI Usage

### Installation & Global Setup

```bash
# Clone or navigate to the repository
git clone https://github.com/vecyang1/poppy-cli.git
cd poppy-cli

# Link globally (ensures ~/.local/bin/poppy is in your $PATH)
chmod +x bin/poppy
ln -sf $(pwd)/bin/poppy ~/.local/bin/poppy

# Verify global installation
command -v poppy
```

### CLI Commands

#### 1. Board Operations

```bash
# List all user boards
poppy boards list

# Inspect a board's full node and edge hierarchy as an ASCII tree
poppy boards get polished-sea-2LmlU

# Export board content and connections to Markdown
poppy boards export polished-sea-2LmlU -o export.md
```

#### 2. AppSumo Community Intelligence

```bash
# View sentiment ratio, taco distribution, strengths, and friction points
poppy reviews summary

# Filter reviews by rating or keyword
poppy reviews list --limit 5 --min-rating 5
poppy reviews list --search "youtube"

# Browse community Q&As and founder answers
poppy questions list --limit 5 --search "api"

# View 6-tier AppSumo pricing and feature comparison matrix
poppy tiers
```

#### 3. Diagnostic Reconciliation

```bash
# Run 6-point live diagnostic health check
poppy diagnose
```

---

## 🏗️ Architecture & Reverse-Engineered Findings

### 1. Frontend & Realtime Layer
- **Framework**: Next.js App Router with React Server Components (Turbopack bundler).
- **Canvas Engine**: React Flow (`.react-flow`) managing 2D node graphs.
- **Rich Text**: Tiptap / ProseMirror document structures.
- **Live Collaboration**: Liveblocks (`liveblocks.io`) for multi-user cursor tracking.

### 2. Authentication & Data Layer
- **Authentication**: Clerk Authentication (`sess_...`) bridging to Firebase Custom Auth tokens.
- **Backend Database**: Google Cloud Firestore (`projects/poppy-ai-16252/databases/(default)`).
- **Core Collections**:
  - `graphs/{graphId}`: Canvas nodes (`nodesV2`, `nodes`) and edges (`edgesV2`, `edges`).
  - `boards/{boardId}`: Board metadata, folders, and ownership.

For full schema definitions and REST query specifications, refer to [API.md](API.md).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
python3 -m unittest discover tests
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
