# Template Contract

Use this file when installing templates or rendering HTML.

## Installed Template Assets

The skill must carry three empty page templates:

```text
assets/page-templates/
  library-empty.html
  book-home-empty.html
  chapter-page-empty.html
```

The first-run initializer copies them into:

```text
<project>/.book-analyst/page-templates/
```

The project must also receive empty JSON skeletons:

```text
<project>/.book-analyst/data-skeletons/
  manifest.empty.json
  analysis/book.empty.json
  analysis/themes.empty.json
  analysis/concepts/index.empty.json
  analysis/chapters/index.empty.json
  analysis/chapters/chapter.empty.json
  analysis/evidence/index.empty.json
```

## Required Render Variables

When rendering HTML, replace these template variables:

| Variable | Used by | Meaning |
| --- | --- | --- |
| `{{BOOKS_JSON}}` | Library | JSON array returned by metadataStore or `/api/books`. |
| `{{BOOK_JSON}}` | Book Home | `analysis/book.json`. |
| `{{THEMES_JSON}}` | Book Home | `analysis/themes.json`. |
| `{{CHAPTERS_JSON}}` | Book Home | `analysis/chapters/index.json`. |
| `{{EVIDENCE_JSON}}` | Book Home / Chapter Page | `analysis/evidence/index.json`. |
| `{{CHAPTER_JSON}}` | Chapter Page | `analysis/chapters/chXX.json`. |
| `{{LIBRARY_HREF}}` | Book Home / Chapter Page | Link back to Library. Use `/` in Flask mode. |
| `{{BOOK_HOME_HREF}}` | Chapter Page | Link back to the current book home. |

## Page Responsibilities

### Library

Manage many books. Do not explain a single book.

Slots:

- poster/list view
- upload
- search
- status filters
- parse filters
- language filter
- sort
- metadata cards

### Book Home

Show the God's-eye view of one book.

Slots:

- `BookIdentity`
- `BookThesis`
- `ThemeMap`
- `ChapterHeatmap`
- `ThemeEvidence`
- `ConceptNetwork`
- `FrameworkShelf`
- `ReflectionDock`

Theme selection must update a large content region, not just a small text area.

### Chapter Page

Explain one high-value chapter's argument.

Slots:

- `ChapterTopNav`: Home icon to Library, Back button to Book Home
- `ChapterIdentity`
- `ChapterRole`
- `OverviewCanvas`
- `ArgumentCanvas`
- `FrameworkCanvas`
- `CaseCanvas`
- `ResearchCanvas`
- `MethodCanvas`
- `EvidenceDrawer`

No complete breadcrumb. The page should keep navigation light.

## Empty Data Rule

If a module has no data, do not render that module.

Acceptable empty state:

- whole book is not parsed yet
- a page template is opened before data injection

Unacceptable:

- large empty cards inside a generated book page
- fake labels or fake reading modes
- filler tags without source

## Evidence Drawer Rule

Main cards stay compact. Evidence detail moves into `EvidenceDrawer`.

Drawer fields:

- source range
- evidence type
- short quote or source hint
- evidence summary
- why it matters
- AI interpretation
- read location
