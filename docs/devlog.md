# Devlog

## Day 1 - D1-03

Implemented the Markdown loader for the FastAPI documentation corpus.

### Result

- Loaded 156 Markdown documents.
- Preserved relative source paths.
- Extracted heading hierarchy and line numbers.
- Ignored headings inside fenced code blocks.
- Removed explicit Markdown heading anchors from titles.