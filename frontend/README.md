# Sentinel RAG — frontend

Next.js app for the Sentinel RAG lab. Three screens, all talking to the Python
backend on `http://127.0.0.1:8000`:

- **Ask** (`/`) — runs one query and streams the pipeline over SSE (fetch-stream), animated step cards, answer + citations.
- **Compare** (`/strategy`) — one query on two chunking strategies side by side.
- **Documents** (`/documents`) — upload `.md`/`.txt`/`.pdf`, list, delete, reindex.

See the [root README](../README.md) for the full design and backend setup.

## Run

```bash
pnpm install
pnpm dev      # http://localhost:3000  (backend must be running on :8000)
pnpm build    # typecheck + production build
```

`NEXT_PUBLIC_API_BASE` overrides the backend URL (default `http://127.0.0.1:8000`).
The backend allows CORS from `http://localhost:3000`; there is no Next.js API proxy.
