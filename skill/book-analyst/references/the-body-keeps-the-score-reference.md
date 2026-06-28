# The Body Keeps the Score — Reference Output Structure

Benchmark book analysis. Manually crafted by Ezri + AI (not pipeline-generated).
Use this as the aspirational output template.

## Vault File Structure

```
5.0 Books & Reading/Books/The Body Keeps the Score/
├── The Body Keeps the Score.md         ← Main note
├── Phase 1 - God's-eye View.md         ← Skeleton analysis
├── Phase 2 - Chapter Value Grading.md  ← Value grading table
├── Ch 10 - Developmental Trauma.md     ← Deep chapter analysis
├── source/原文.txt                     ← Full text
└── web/
    ├── index.html                      ← Architecture page
    ├── poster-wall.html                ← Poster wall entry
    └── chapters/
        ├── ch01-*.html
        ├── ch04-*.html
        ├── ch05-*.html
        ├── ch06-*.html
        ├── ch07-*.html
        ├── ch09-*.html
        ├── ch10-*.html
        ├── ch11-*.html
        ├── ch14-*.html
        └── ch15-*.html
```

## Key Design Decisions

### Bilingual Titles
Every chapter carries BOTH the English original title AND Ezri's Chinese naming.
These are NOT translations — they're personal working labels.
Pipeline default should be English-only; Chinese names added during Phase 4.

### Personal Connection Layer
Every major section has a "与你的关联" (relevance to you) annotation.
These are specific to Ezri's life context and CANNOT be automated.
Pipeline must NOT fake these — leave blank or "[待补充]".

### Source Citations
Chapter detail pages have a source drawer (drawer-backdrop + drawer JS).
Citations reference exact passages from the source.txt with line ranges.
This precision requires manual verification — pipeline should cite at chapter level only.

### Grading Matrix (Phase 2)
Scoring: ⭐⭐⭐ (must-read) / ⭐⭐ (skim) / ⭐ (skip)
Each grade has a personal reason column written by Ezri, not AI.
Pipeline can auto-suggest grades but must flag them as suggestions the user can override.

### Web Index Architecture
- Hero section with thesis card
- Chapter navigation bar (links to detail pages)
- "Your Must-Read Clusters" — chapters grouped by theme with EN+CN titles
- Full-book heatmap (all chapters color-coded)
- Cross-chapter Concept Map
- Complete grading matrix table

### Detail Page 5-Tab Layout
1. **Overview** — grid of notes cards with key points
2. **Causal Chain** — interactive step-by-step sequence
3. **Frameworks** — accordion-styled named frameworks
4. **Cases** — story cards with source attribution chips
5. **Research + Decision Rules** — timeline + decision rules + key takeaways

## CSS Theme
"warm-paper" — variables use --ink, --paper, --line, --gold, --red, --blue, --green
Fonts: Songti SC (body), PingFang SC (display)
Background: radial gradient + linear gradient
