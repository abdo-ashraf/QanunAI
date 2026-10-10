# QanunAI Frontend

React + TypeScript chat UI for the QanunAI backend (Arabic legal Q&A over the
Egyptian Civil Code of 1948).

## Stack

- React 19 + Vite + TypeScript
- TanStack Query for server state
- Zod for runtime validation of API responses
- shadcn/ui primitives + [ai-elements](https://ai-sdk.dev/elements) for AI UI
- Lightweight local i18n (Arabic RTL default, English LTR toggle)

## Structure

```
src/
  components/
    ui/                 shadcn/ui primitives
    ai-elements/        ai-elements components (conversation, message, prompt-input, sources, ...)
    language-toggle.tsx
  features/
    legal-assistant/
      api/              Zod schemas + fetch functions (rag.ts, health.ts)
      components/       chat view, composer, messages, sources, header
      hooks/            use-health, use-legal-assistant
      legal-assistant-page.tsx
      types.ts
  lib/                  api client, i18n dictionary, utils
  providers/            LanguageProvider, QueryProvider
```

## Run locally

The backend must be running. Start it first:

```bash
cd ../qanunai_backend
python -m uv run --env-file .env uvicorn presentation.app:app --host 0.0.0.0 --port 8000
```

Then:

```bash
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` and `/health` to
`http://localhost:8000` (see `vite.config.ts`), so no CORS setup is needed in
development.

## Configuration

Copy `.env.example` to `.env` only when the API is served from a different
origin (e.g. production):

```
VITE_API_BASE_URL=https://api.example.com
```

When `VITE_API_BASE_URL` is empty (default), requests are sent relative to the
app origin and rely on the dev proxy or a reverse proxy.

The backend allows browser origins listed in its `CORS_ALLOW_ORIGINS`
(defaults to `http://localhost:5173`).

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — type-check and build to `dist/`
- `npm run lint` — run oxlint
- `npm run preview` — preview the production build
- `npm run ai:elements` — add more ai-elements components

## Notes

- The backend is synchronous and stateless (no streaming, no conversation
  history), so the chat transcript is kept in memory only and cleared on reload
  or via "New chat".
- `MessageResponse` uses Streamdown without the syntax-highlighting / math /
  mermaid plugins to keep the bundle small. Re-add them in
  `src/components/ai-elements/message.tsx` if richer markdown is needed.
