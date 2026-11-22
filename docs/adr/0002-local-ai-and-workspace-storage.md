# ADR-0002: Local AI provider and workspace-scoped document storage

- **Status:** Accepted for local development; hosted tenancy remains unresolved
- **Date:** 2026-11-22
- **Decision owners:** Yuktara Technologies engineering

## Context

The product is designed for local-first document processing. The prototype previously had a misleading extractive answer engine and a global vector index. A local user needs multiple documents without accidentally mixing separate browser workspaces.

## Decision

- Use Sentence Transformers as the explicit semantic embedding provider, configured for local-only model loading by default.
- Support Ollama as the local generative answer provider through a configurable base URL, model name, timeout, and startup readiness check.
- Retain the extractive TF-IDF sentence selector only as an explicitly identified non-generative fallback.
- Scope local NumPy indexes by validated workspace ID and tag chunks with server-generated document IDs.
- Store vectors and document metadata together in one atomically replaced archive, with in-process synchronization.
- Preserve legacy routes and the historical default index while the frontend migrates to the versioned API.

## Security boundary

A client-generated workspace ID is a storage namespace, not authentication or authorization. It must never be treated as a tenant identity in a hosted deployment. Hosted multi-user mode requires authenticated principals, authorization checks, tenant-scoped persistence, and process-safe transactional storage before release.

## Alternatives considered

- **Remote hosted LLM APIs:** not the default because local inference is the product's privacy and offline direction.
- **Microservice vector database:** deferred until scale, concurrent writers, or multi-host deployment justify the operational cost.
- **Extractive engine as the primary model:** rejected because it cannot perform genuine generative synthesis and must not be described as an LLM.

## Consequences

- Local users can index and delete multiple documents within a browser workspace.
- Ollama must be installed and the configured model available for generative mode.
- Embedding model weights must be cached before strict offline startup.
- The current storage adapter is not safe for concurrent writes from multiple server processes.
- Page-aware citations, OCR, hosted identity, and transactional storage remain explicit release gates.
