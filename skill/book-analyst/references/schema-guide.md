# Schema Guide

Use this file when filling JSON data.

## File Set

```text
manifest.json
analysis/book.json
analysis/themes.json
analysis/concepts/index.json
analysis/chapters/index.json
analysis/chapters/chXX.json
analysis/evidence/index.json
```

## Book

Required fields:

- `id`
- `title`
- `author`
- `language`
- `thesis`
- `coreQuestion`
- `readingRoute`
- `stats`

Only use tags that come from metadata or analysis. Do not invent marketing categories.

## Theme

Required fields:

- `id`
- `title`
- `oneLine`
- `whyRead`
- `readingOrder`
- `whatYouGet`
- `chapterIds`
- `conceptIds`
- `evidenceIds`

The Book Home right-side or detail region must update when a theme is selected.

## Chapter Index Entry

Required fields:

- `id`
- `number`
- `originalTitle`
- `readerTitle`
- `roleInBook`
- `valueDensity`
- `recommendation`
- `themeIds`
- `sourceRange`

Only add `detailPage` when a chapter detail HTML exists.

## Chapter Detail

Required arrays:

- `roleCards`
- `overviewCards`
- `argumentChain`
- `frameworks`
- `cases`
- `research`
- `decisionRules`

Arrays can be empty, but empty arrays must not render visible modules.

Every overview card, chain node, case, research item, and decision rule needs `sourceRef` or `evidenceRefs`.

## Evidence

Required fields:

- `id`
- `type`
- `title`
- `sourceRange`
- `summary`
- `whyImportant`
- `aiUnderstanding`
- `readLocation`
- `supports`

Optional fields:

- `shortQuote`
- `sourceHint`

Use `shortQuote` only when a compliant, verified short quote exists. Otherwise use `sourceHint`.

## Validation Checklist

- No unresolved `sourceRef`.
- No source-less author claim.
- No full-length copyrighted excerpt.
- No personal value claims unless Phase 4 data exists.
- No empty rendered modules.
- No chapter detail page for low-value chapters unless the user explicitly requested it.

## Generated Book Knowledge Skill

When creating a downstream skill from a finished book analysis, use:

```bash
python skill/book-analyst/scripts/generate_book_skill.py analysis/<book-id> --output-root generated-skills
```

Only include:

- thesis
- core question
- concepts
- evidence summaries
- source ranges
- AI interpretation clearly labeled as interpretation

Do not include:

- long original passages
- unverified quotes
- private user reflections unless explicitly requested
