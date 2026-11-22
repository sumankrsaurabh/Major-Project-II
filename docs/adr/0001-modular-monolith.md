# ADR-0001: Modular monolith for the first production architecture

- **Status:** Accepted
- **Date:** 2026-11-22
- **Decision owners:** Yuktara Technologies engineering

## Context

ChatWithPDF is a small product with a React client, FastAPI backend, local model runtime, document ingestion, retrieval, and conversation workflows. The team needs clear ownership boundaries and testability without introducing distributed-systems operations before there is a measured need.

## Decision

Keep the backend as a modular monolith. Separate API adapters, application use cases, domain rules, and infrastructure providers as the code is migrated. Keep the frontend organized by product feature with shared UI and API primitives. Introduce explicit interfaces around embeddings, vector indexes, PDF extraction, LLM generation, and persistence.

## Alternatives considered

- **Microservices:** rejected for now because there is no demonstrated scaling or team-ownership requirement that offsets deployment and operational complexity.
- **A single unstructured application module:** rejected because it makes business rules, provider choices, and UI concerns difficult to test and replace.

## Consequences

- One deployable backend remains straightforward for local-first installation.
- Infrastructure can be replaced without rewriting product workflows.
- New functionality must respect dependency direction and be accompanied by tests.
- Service extraction can be reconsidered only with measured scaling, reliability, or ownership evidence.
