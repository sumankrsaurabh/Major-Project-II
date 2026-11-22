# ChatWithPDF Product UI Standard

**Product:** ChatWithPDF  
**Brand:** Yuktara Technologies  
**Status:** Design and implementation standard

## 1. Product experience

ChatWithPDF is a document workspace, not a generic chatbot. The interface must keep the source document, conversation, and evidence connected.

Primary user journey:
1. Create or open a workspace.
2. Add one or more PDF documents.
3. See processing progress and extraction warnings.
4. Ask a question about the selected document scope.
5. Read an answer with numbered citations.
6. Select a citation to open the PDF at the cited page.
7. Continue the conversation or manage the source documents.

## 2. Information architecture

Primary navigation:
- **Workspace** — recent workspaces and quick create.
- **Documents** — uploaded PDFs, indexing status, search, metadata and actions.
- **Chat** — active conversation and source scope.
- **Insights** — document summary, extracted topics and key information.
- **Settings** — local model, embedding model, storage, privacy and diagnostics.

Workspace navigation is the primary context. Avoid a navigation item for internal developer tools in the end-user experience; diagnostics belong under Settings or an explicitly enabled developer mode.

## 3. Desktop workspace layout

Use a three-region workspace at wide desktop sizes:
- Left navigation rail/sidebar: 240–264 px.
- Document canvas: flexible, typically 45–55% of available content width.
- Conversation panel: flexible, typically 45–55%.

The PDF and chat panels should be resizable. On narrow screens, use a single-column layout with explicit tabs for Document and Chat. Do not force a desktop three-column layout onto mobile.

## 4. Visual language

The product should feel calm, precise, and professional. Avoid excessive glow, gradients, glass effects, and decorative motion.

### Design tokens

| Token | Default | Usage |
|---|---|---|
| `color.canvas` | `#F7F8FA` | Main light canvas |
| `color.surface` | `#FFFFFF` | Panels and cards |
| `color.text` | `#171A20` | Primary text |
| `color.muted` | `#687180` | Secondary text |
| `color.border` | `#E5E8ED` | Dividers and outlines |
| `color.brand` | `#3157D5` | Primary actions and active states |
| `color.success` | `#16835D` | Completed state |
| `color.warning` | `#A96812` | Warnings |
| `color.danger` | `#C43D42` | Errors and destructive actions |

Dark mode must use a separately defined semantic token set. Do not invert colors mechanically.

### Typography

- UI family: Inter or system sans-serif.
- Body: 14–16 px with 1.45–1.6 line height.
- Secondary labels: 12–13 px.
- Page title: 24–30 px, semibold.
- Avoid using display fonts for dense document text.
- PDF page rendering must preserve the source document's typography.

### Shape and spacing

- Use a 4 px spacing base.
- Inputs and buttons: 8–10 px radius.
- Cards and panels: 10–14 px radius.
- Use subtle 1 px borders; reserve shadows for layered surfaces.
- Keep content density high enough for professional document work without crowding.

## 5. Core components

Build reusable, accessible components:
- AppShell, Sidebar, WorkspaceHeader
- Button, IconButton, Input, SearchField, Select, Dialog, Menu
- DocumentCard, DocumentList, DocumentStatus, UploadDropzone
- PdfViewer, PdfToolbar, PageNavigator, TextSelectionToolbar
- ChatThread, MessageBubble, Composer, StreamingIndicator
- CitationChip, CitationList, SourcePreview
- EmptyState, ErrorState, Skeleton, Toast, ProgressBar
- SettingsSection, ModelStatus, StorageUsage

Each component must have documented variants, disabled/loading states, keyboard behavior, and accessibility labels.

## 6. Required UI states

Every asynchronous feature must define:
- Initial/empty state
- Loading state
- Success state
- Recoverable error state
- Terminal error state
- Retry or recovery action
- Disabled state where applicable

Document status vocabulary:
- Queued
- Uploading
- Extracting
- OCR processing
- Indexing
- Ready
- Failed

Never report a document as Ready before the vector index and metadata have been persisted successfully.

## 7. Chat and citation behavior

- Clearly distinguish user, assistant, and system status messages.
- Render Markdown safely; do not render arbitrary HTML from model output.
- Citations must be interactive and identify filename and page.
- Clicking a citation opens the correct document and page.
- If a response has no supporting citations, label it as general guidance or insufficiently grounded.
- Preserve conversation scope and visibly show which documents are included.
- Provide stop-generation, retry, copy, and clear-conversation actions where supported.
- Do not show fabricated confidence percentages.

## 8. Upload and document management

- Accept PDF using both drag-and-drop and a browse button.
- Validate before upload and show configured size limits.
- Show upload progress separately from server-side processing progress.
- Explain OCR and extraction warnings in plain language.
- Support cancel/retry where the backend supports it.
- Provide rename, download, and delete actions only when implemented and authorized.
- Confirm destructive actions and explain their effect on derived index data.

## 9. Accessibility and responsive quality

- Use semantic landmarks and heading hierarchy.
- All controls must be keyboard operable with visible focus.
- Icon-only controls require accessible names.
- Maintain WCAG AA contrast for text and interactive states.
- Announce upload and processing status to assistive technology.
- Respect reduced-motion preferences.
- Test at 360 px, 768 px, 1024 px, and 1440 px widths.

## 10. UI acceptance criteria

A UI feature is accepted only when:
- It follows the product information architecture.
- It uses semantic design tokens and shared components.
- Empty, loading, error, and success states are implemented.
- Keyboard and screen-reader interactions are checked.
- It works at mobile and desktop breakpoints.
- API behavior is tested independently of presentation.
- Screenshots or recordings are attached to the pull request.
