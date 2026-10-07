# Poppy AI Reverse-Engineered Architecture & API Specification

## 1. Authentication Contract

Poppy AI utilizes a hybrid authentication architecture combining **Clerk** (front-facing identity, sessions, and social logins) and **Google Firebase Custom Auth** (backend database access):

1. **Clerk Client Session**:
   - `window.Clerk.session.id`: e.g. `sess_3KKdcgZ1q1hEfUzuJinJJqZ8Csx`
   - `window.Clerk.session.getToken()`: Returns RSA-256 signed Clerk JWT (`tokenPrefix: eyJhbGciOiJSUzI1NiIs...`).
2. **Firebase Custom Token Minting**:
   - Clerk mints a Firebase custom auth token via a Next.js Server Action (`_next/data` / API route).
   - Firebase Auth SDK signs in using `signInWithCustomToken()`.
   - Credentials persisted in browser `IndexedDB` under `firebaseLocalStorageDb/firebaseLocalStorage`.
   - `stsTokenManager.accessToken`: Google OAuth 2.0 Bearer token granting access to Firestore.

---

## 2. Google Cloud Firestore Specifications

- **GCP Project ID**: `poppy-ai-16252`
- **Database**: `(default)`
- **REST Base URL**: `https://firestore.googleapis.com/v1/projects/poppy-ai-16252/databases/(default)/documents`

### Collection: `graphs` (Canvas Data)

Every board maps to a graph document in `graphs/{graphId}`:

```json
{
  "documentId": "BNW7aGRhauOFL1L5SKFi",
  "viewport": {
    "x": -120.5,
    "y": 450.2,
    "zoom": 0.85
  },
  "nodesV2": [...],
  "edgesV2": [...],
  "dateCreated": "2026-10-07T12:13:13.706Z",
  "dateUpdated": "2026-10-07T13:37:40.926Z"
}
```

### Canvas Node Types & Schemas

| Node Type | Purpose | Key Attributes |
| :--- | :--- | :--- |
| `groupNode` | Visual bounding container for functional areas | `title`, `width`, `height`, `zIndex: -1` |
| `chatNode` | AI intelligence core / chat dialogue hub | `title`, incoming `connectionEdge` targets |
| `documentNode` | Text / strategy framework notes | `title`, `data.content` (ProseMirror JSON) |
| `textNode` | Inline canvas text cards / instructions | `title`, step-by-step guidance |
| `youtubeNode` | Ingested YouTube video with transcript | `title`, `data.url`, `data.thumbnailUrl` |
| `webScrapperNode`| Ingested web page / article scrape | `title`, `data.url`, `data.text` |
| `annotationNode` | Sticky comments & feedback callouts | `title`, author, timestamp |

### Edge Contract (`connectionEdge`)

```json
{
  "id": "groupNode-123-chatNode-456",
  "source": "groupNode-wonderful-wave-lu9jW",
  "sourceHandle": "connector",
  "target": "chatNode-young-thunder-FnpUb",
  "targetHandle": "chat-connector",
  "type": "connectionEdge",
  "animated": true
}
```

---

## 3. Realtime Multiplayer Layer (Liveblocks)

Poppy AI synchronizes real-time user presences, mouse cursors, and active drag states through Liveblocks:
- **WebSocket Endpoint**: `wss://liveblocks.net/v2/rooms/...`
- **Room Identity**: `board_{boardId}`
- **Synced Properties**: `activeUserData`, `userActivity`, live cursor coordinate streams.
