# Mnemosyne

> **The Mother of Memory** · Your personal reading companion.
> Mnemosyne (Greek: Μνημοσύνη) was the Titaness of memory and the mother of the nine Muses.
> This project is your second brain for books — every read, every note, every connection.

## What It Does

```
📚 Books arrive (EPUB / PDF / MOBI / TXT)
   ↓
🔄 Hermes converts to text, detects chapters
   ↓
🧠 Analyzer extracts frameworks, cases, decisions, research
   ↓
🎨 Generator renders Architecture HTML (god's-eye view + chapter detail)
   ↓
🖼️ Poster wall shows your whole library, filterable by status / language / rating
   ↓
🔗 Syncs with your Obsidian vault via git (Golden-House repo)
```

## Architecture

```
   ┌─────────────────────────────────────┐
   │   GitHub: Golden-House (vault)      │  ← single source of truth
   └──────────┬──────────────────┬───────┘
              │ git              │ git
       ┌──────┴──────┐    ┌──────┴──────┐
       │ Mac (local) │    │  VPS server │
       │ Hermes      │    │ Flask app   │
       │ Obsidian UI │    │ Calibre     │
       │ Daily use   │    │ Public web  │
       └─────────────┘    └─────────────┘
```

## Project Structure

```
Mnemosyne/
├── app/                     Flask app (poster wall + upload API + book pages)
│   └── ...
├── analyzer/                Book analysis logic (chapter_template, convert, sync)
├── static/
│   ├── templates/           HTML templates (poster-wall, chapter, book page)
│   └── assets/              Static assets
├── data/                    Runtime data (NOT in git)
│   ├── books/               Source files (EPUB/PDF/MOBI)
│   ├── generated/            Generated HTML output
│   └── covers/               Cached book covers
├── scripts/                 Operational scripts (sync, deploy, etc.)
├── tests/                   Test suite
├── logs/                    Runtime logs
├── docker-compose.yml       Container orchestration
└── README.md
```

## Quick Start (Local Development)

```bash
# 1. Clone & setup
git clone https://github.com/Ezri-Lin/Mnemosyne.git
cd Mnemosyne

# 2. Install Python deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Install Calibre (for ebook conversion)
brew install calibre  # macOS
# apt install calibre  # Ubuntu

# 4. Run Flask app
python -m app.server
# → http://localhost:5000
```

## Deploy to VPS (Ubuntu 24)

```bash
# On the VPS:
ssh user@vps
git clone https://github.com/Ezri-Lin/Mnemosyne.git
cd Mnemosyne
docker compose up -d
# → https://reading.yourdomain.com
```

## Sync with Obsidian Vault

```bash
# Pull latest from Golden-House vault
./scripts/sync_vault.sh

# This:
# 1. git pulls latest from Golden-House repo
# 2. Updates local book status / metadata from vault frontmatter
# 3. Re-runs analysis on changed books
```

## License

Private project. Not for redistribution.
