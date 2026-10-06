# Design Decisions

## D1-03 Markdown Loader

- The corpus is stored as Markdown files from the FastAPI documentation source.
- The loader keeps the relative source path as metadata.
- Heading hierarchy is extracted from Markdown headings.
- Explicit heading anchors such as `{ #section-name }` are removed from heading titles.
- Headings inside fenced code blocks are ignored.