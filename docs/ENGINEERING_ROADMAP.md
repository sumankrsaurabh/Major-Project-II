# ChatWithPDF Engineering Roadmap

This roadmap is intentionally incremental. Existing functionality is not considered production-ready merely because it exists in the repository; each milestone requires tests and evidence.

## P0 — Repository and runtime stabilization

- [ ] Inventory every backend route, frontend screen, dependency, and data directory.
- [ ] Add baseline tests for existing upload, status, chat, and clear-conversation behavior.
- [x] Verify frontend core API paths and response schemas against the versioned FastAPI surface; keep broader endpoint contract coverage in CI.
- [ ] Replace wildcard CORS and correct health/readiness semantics.
- [ ] Enforce upload size and content validation consistently.
- [x] Ensure temporary uploads are cleaned on success and failure without deleting active requests' files.
- [x] Remove import-time NLTK corpus downloads and add deterministic offline tokenization fallbacks.
- [x] Add reproducible setup instructions and `.env.example`.

**Exit criteria:** a new engineer can install and run the app using documented steps; baseline tests and frontend production build pass.

## P1 — Maintainable architecture

- [ ] Introduce validated application settings.
- [x] Introduce versioned API v1 compatibility routes while preserving legacy route aliases.
- [ ] Complete typed response/error contracts across every public endpoint.
- [ ] Create application/domain/infrastructure boundaries.
- [ ] Move existing behavior behind use cases and adapters.
- [ ] Add dependency injection and remove unnecessary global mutable state.\n- [x] Defer optional analysis-service construction until an analysis endpoint is first used.
- [ ] Add Python lint/format/type-check configuration.
- [ ] Add frontend feature folders and shared design tokens.

**Exit criteria:** new features can be added without placing business logic in route handlers or UI components.

## P2 — Reliable local AI and RAG

- [x] Implement configurable local Ollama provider with base URL, model, timeout, and startup readiness check.
- [ ] Add runtime smoke tests against an installed Ollama model.
- [ ] Clearly distinguish extractive fallback from generative model output.
- [ ] Implement embedding provider contract and explicit model identity.
- [ ] Implement FAISS adapter with safe persistence and index metadata.
- [ ] Add lexical + semantic retrieval and measured reranking.
- [ ] Preserve document ID, page, and chunk ID through retrieval.
- [ ] Return verifiable citations and handle insufficient evidence.
- [ ] Add prompt-injection defenses for untrusted document content.

**Exit criteria:** deterministic retrieval tests pass and answers cite actual source pages; provider outages produce actionable errors.

## P3 — Document ingestion

- [ ] Page-aware PDF extraction.
- [ ] OCR fallback for image-only or low-text pages.
- [ ] Configurable limits for file size, page count, and processing duration.
- [ ] Structure-aware chunking and batch embedding.
- [ ] Ingestion state, progress, retry, and cancellation semantics.
- [ ] Document deletion cascades to metadata, files, chunks, and vectors.
- [ ] Corrupt, encrypted, empty, and malformed PDF tests.

**Exit criteria:** text PDFs and scanned PDFs can be ingested, queried, deleted, and re-indexed reliably.

## P4 — Product-grade UI

- [ ] Establish Yuktara design tokens and component standards.
- [ ] Build responsive application shell and navigation.
- [ ] Build document library with search, sorting, status, and actions.
- [ ] Build PDF viewer with page navigation and text selection.
- [ ] Build chat workspace with streaming-ready message model.
- [ ] Build clickable citations that navigate to source pages.
- [ ] Add upload progress, ingestion status, retry, and clear error states.
- [ ] Add settings for model, storage, privacy, and diagnostics.
- [ ] Add keyboard navigation, screen-reader labels, and contrast checks.

**Exit criteria:** primary workflows work on desktop and mobile widths, with complete loading/empty/error/success states.

## P5 — Release and operations

- [ ] Authentication and tenant isolation for hosted deployment.
- [ ] Request IDs, structured logs, metrics, and dependency health.
- [ ] Backup, restore, and index rebuild procedure.
- [ ] CI for lint, tests, security checks, and production builds.
- [ ] Dependency pinning and vulnerability review.
- [ ] Performance tests for upload, indexing, retrieval, and chat.
- [ ] Threat model, privacy notice, retention policy, and release checklist.

**Exit criteria:** a release candidate passes automated gates, security review, and documented manual smoke tests.

## Release rule

Do not market the system as production-ready until the relevant exit criteria are demonstrated. Keep local single-user mode and hosted multi-user mode as separate deployment profiles with different security requirements.
