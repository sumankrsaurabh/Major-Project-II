# Contributing to ChatWithPDF

This repository is maintained by Yuktara Technologies. The goal is a codebase that every engineer can understand, test, and safely change.

## Working agreement

1. Read `README.md`, `docs/ARCHITECTURE.md`, and the relevant feature documentation before changing code.
2. Keep pull requests focused. One feature, fix, or refactor per PR.
3. Do not mix formatting-only changes with behavior changes.
4. Preserve public API behavior unless the PR explicitly documents a versioned migration.
5. Add or update tests for every behavior change.
6. Never commit secrets, real user documents, generated indexes, model weights, or local environment files.
7. Update documentation when setup, configuration, API behavior, or architecture changes.

## Branch naming

- `feat/<short-description>`
- `fix/<short-description>`
- `refactor/<short-description>`
- `docs/<short-description>`
- `test/<short-description>`
- `chore/<short-description>`

## Commit messages

Use concise imperative messages with a conventional prefix:

- `feat: add page-level citation navigation`
- `fix: reject malformed PDF uploads`
- `refactor: isolate vector index adapter`
- `test: cover document ownership checks`
- `docs: explain local model setup`

## Code organization

- Put HTTP concerns in API endpoint modules.
- Put workflows in application use cases.
- Put business rules and stable types in domain modules.
- Put third-party integrations in infrastructure adapters.
- Keep React feature code inside its feature directory.
- Put reusable, domain-neutral UI in `shared/components`.
- Avoid circular imports and hidden global mutable state.
- Prefer dependency injection over importing concrete infrastructure into business logic.

## Python standards

- Add type hints to public functions and service boundaries.
- Use Pydantic for external input validation and explicit domain types internally.
- Use structured logging; do not use `print` for application diagnostics.
- Catch expected exceptions at boundaries. Do not silently swallow unexpected failures.
- Keep configuration in validated settings; do not scatter environment reads.
- Never log document text, prompts, credentials, or sensitive metadata.

## Frontend standards

- Use functional components and feature-owned hooks.
- Keep network calls in feature API modules.
- Model loading, empty, success, and error states explicitly.
- Ensure keyboard access, visible focus, labels, and semantic HTML.
- Avoid inline styling for shared design tokens and reusable components.
- Keep components small and name them by product responsibility.

## Pull request checklist

- [ ] Scope and user impact are explained.
- [ ] Architecture boundaries are respected.
- [ ] Tests cover success, failure, and edge cases.
- [ ] Python lint/tests pass.
- [ ] Frontend lint/build/tests pass.
- [ ] API contracts and documentation are updated.
- [ ] No secrets, private documents, or generated artifacts are included.
- [ ] Security, privacy, accessibility, and performance implications are considered.
- [ ] Screenshots or a short recording are attached for UI changes.

## Definition of done

A task is done only when implementation, tests, documentation, error handling, and review notes are complete. A feature that works only on the author's machine is not done.
