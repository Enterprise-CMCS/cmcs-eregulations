# eRegs Agent Notes

This repo is a Django + Vue monorepo with multiple Lambda services and CDK deploys. Use this as a high-signal map for safe edits.

## What Lives Where
- `solution/backend/`: Django app/API. Main apps: `regcore` (reg text + parser ingest), `regulations` (site views/templates), `resources` (sidebar content), `content_search` (hybrid keyword/semantic search).
- `solution/ui/regulations/eregs-vite/`: SPA build for `/search`, `/subjects`, `/statutes`, `/manual`, `/pl119-21`.
- `solution/ui/regulations/eregs-component-lib/`: Vue component library + `eregs-main.iife.js` bundle used by Django-rendered pages (notably reader view).
- `solution/text-extractor/`, `solution/parser/`, `solution/mcp-server/`, `solution/lambda-proxy/`: separate Lambda/service codebases.
- `cdk-eregs/`: AWS CDK stacks. `.github/workflows/deploy-to-env.yml` is the real deploy orchestration source.

## Non-Obvious Architecture Facts
- Django root URL includes both `regcore.urls` and `regulations.urls` at `""`; include order matters for route collisions.
- Most APIs are under `/v3/`, but ownership is split across apps (`regcore`, `resources`, `content_search`, some `regulations` views).
- `manage.py` defaults to `cmcs_regulations.settings.deploy` (not local). Set settings explicitly when running local scripts directly.
- Reader page is SSR for reg text, then Vue sidebar hydrates and fetches resources/context banners client-side.
- `content_search` uses raw SQL CTEs + Postgres FTS + `pgvector`; avoid refactors that assume generic ORM-only behavior.

## Local Commands (Source of Truth: `solution/Makefile`)
- Start local stack + seed core sample regs: `cd solution && make local`
- Build static assets for Django/admin: `cd solution && make local.collectstatic`
- Create admin user: `cd solution && make local.createadmin`
- Stop/clean local: `cd solution && make local.stop` / `cd solution && make local.clean`
- Watch frontend + extractor changes: `cd solution && make watch-all`

## Focused Verification Commands
- Python tests (all): `cd solution && make test.pytest`
- Python single test: `cd solution && docker compose exec regulations uv run pytest -v path/to/test_file.py::test_name`
- Vitest (all): `cd solution && make test.vitest`
- Vitest single file: `cd solution/ui/regulations && npm run test-vue -- path/to/test.spec.js`
- Cypress: `cd solution && make test.cypress` (requires local stack)
- Parser tests (single module): `cd solution/parser/<dir> && go test -cover ./...`
- Text extractor unit tests: `cd solution && make text-extractor.test`
- Lint JS/TS: `cd solution && make eslint`
- Lint Python: `cd solution/backend && uv run ruff check --preview .` and `cd solution/text-extractor && uv run ruff check --preview .`

## Frontend Build/Bundling Gotchas
- Global SCSS entry: `solution/ui/regulations/css/scss/main.scss` -> `solution/static-assets/regulations/css/main.css`.
- Django base template loads `css/main.css` + `bundles/eregs-component-lib.css`; SPA templates load `vite/index.css`.
- SPA output path: `solution/static-assets/regulations/vite`.
- Component-lib IIFE output path: `solution/static-assets/regulations/bundles/eregs-main.iife.js`.
- If a UI change is on reader/classic Django pages, edit `eregs-component-lib`; if it is `/search|/subjects|/statutes|/manual|/pl119-21`, edit `eregs-vite`.

## Data/Side-Effect Hotspots
- Saving resources triggers signals that recompute grouped/related fields (`resources/models/groups.py`).
- Resource saves also update `content_search.ResourceMetadata` via signals.
- Admin resource saves can trigger text extraction and async index updates.
- Parser part upload can trigger regulation text extraction/indexing callbacks.
- Text extractor callbacks land at `/v3/content-search/resource/<id>/chunk` and `/v3/content-search/reg_text/<id>/chunk`; these endpoints create/update `ContentIndex` chunks.

## Search-Specific Gotchas
- `content_search` query flow is two-stage by design: raw SQL ranking first, then re-query current page for `SearchHeadline` annotation + prefetch. Keep this pattern for performance.
- Result set is polymorphic by design (resource subclasses + indexed regulation text) through unified `ContentIndex`; avoid splitting this into type-specific endpoints unless explicitly required.

## Parser / Lambda Notes
- Parser launcher pulls credentials from AWS Secrets Manager and passes them to eCFR/FR parser Lambdas on invoke.
- `solution/lambda-proxy/` is a local API Gateway shim for Lambda containers (used by local text-extractor/MCP workflows), not a production runtime component.

## Deploy/Infra Guardrails
- Do not hand-edit `cdk-eregs/cdk.out/` or `solution/static-assets/` as source changes.
- Ephemeral deploy naming is deliberate: workflow passes `environment=dev` with `stage_name=eph-<pr>`; do not simplify without checking cleanup workflows.
- Cross-stack exports/imports are tightly coupled by name; keep stack/output naming stable unless updating all dependents.

## Auth Notes (Local vs Deployed)
- OIDC is enabled in settings; local admin commonly uses Django `ModelBackend` + `createsuperuser`.
- Non-prod API Gateway may require basic auth via authorizer; parser/auth behavior depends on `STAGE_ENV`.
