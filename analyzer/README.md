# Mnemosyne Analyzer

## Architecture

The analyzer pipeline transforms a raw book file into structured HTML:

```
Source (EPUB/PDF/MOBI/TXT)
  │
  ├─ 1. convert_book.py     → Convert to TXT (Calibre/poppler)
  ├─ 2. chapter_detect.py   → Split into chapters (regex on "Chapter N")
  ├─ 3. chapter_analyze.py  → AI reads each chapter, extracts:
  │                            frameworks, cases, research, decisions, takeaways
  ├─ 4. chapter_template.py → Generate per-chapter HTML (5 sub-tabs)
  ├─ 5. index_builder.py    → Generate book index.html (architecture + heatmap)
  └─ 6. poster_updater.py   → Update poster wall DB with parse status
```

## Current Status

| Step | File | Status |
|------|------|--------|
| 1. Convert to TXT | `convert_book.py` | TODO |
| 2. Chapter detection | `chapter_detect.py` | TODO |
| 3. AI analysis | `chapter_analyze.py` | TODO (calls Claude/Hermes API) |
| 4. HTML generation | `chapter_template.py` | ✅ Ported from Golden House |
| 5. Index page | `index_builder.py` | TODO |
| 6. Poster update | `poster_updater.py` | TODO (updates SQLite) |

## Usage

```bash
# Full pipeline (triggered by /api/parse/<slug>)
python -m analyzer.pipeline --slug the-body-keeps-the-score --vault /path/to/vault

# Individual steps
python -m analyzer.convert_book --input source.epub --output source.txt
python -m analyzer.chapter_detect --input source.txt --output chapters/
python -m analyzer.chapter_analyze --chapter ch04.txt --output ch04_content.json
python -m analyzer.chapter_template ch04_content.json ch04.html --title "Chapter 4"
python -m analyzer.index_builder --book-dir chapters/ --output index.html
```

## AI Backend

Configure via `.env`:

```
MNEMO_AI_BACKEND=claude    # claude | codex | hermes | openai
ANTHROPIC_API_KEY=sk-...
```

The analyzer calls the AI backend for step 3 (chapter analysis).
All other steps are pure Python (no AI needed).
