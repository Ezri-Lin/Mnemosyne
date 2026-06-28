"""
Mnemosyne configuration.
All settings via env vars (12-factor).
"""
import os
from pathlib import Path

# ============ Paths ============
ROOT = Path(__file__).parent.parent
DATA_DIR = Path(os.environ.get('MNEMO_DATA_DIR', str(ROOT / 'data')))
BOOKS_DIR = DATA_DIR / 'books'
GENERATED_DIR = DATA_DIR / 'generated'
COVERS_DIR = DATA_DIR / 'covers'
LOGS_DIR = ROOT / 'logs'

# ============ Database ============
# Default: SQLite in data/. Override with DATABASE_URL for PostgreSQL/MySQL.
# Examples:
#   postgresql://user:pass@localhost/mnemosyne
#   mysql+pymysql://user:pass@localhost/mnemosyne
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{DATA_DIR / "mnemosyne.db"}')

# ============ Language ============
# Default language for: UI text, generated content, log messages.
# Examples: en, zh, ja, es, fr, de
LANGUAGE = os.environ.get('MNEMO_LANG', 'en')

# Available languages (extensible)
SUPPORTED_LANGUAGES = ['en', 'zh', 'ja', 'es', 'fr', 'de']

# ============ Vault (Golden-House) ============
VAULT_DIR = Path(os.environ.get('VAULT_DIR', str(Path.home() / 'Library/Mobile Documents/iCloud~md~obsidian/Documents/Golden House')))
VAULT_REPO = os.environ.get('VAULT_REPO', 'https://github.com/Ezri-Lin/Golden-House.git')
VAULT_BOOKS_DIR = VAULT_DIR / '5.0 Books & Reading' / 'Books'

# ============ AI / Hermes ============
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
HERMES_ENABLED = bool(ANTHROPIC_API_KEY)

# ============ External APIs ============
ANNA_ARCHIVE_ENABLED = os.environ.get('ANNA_ARCHIVE_ENABLED', 'false').lower() == 'true'
OPENLIBRARY_ENABLED = os.environ.get('OPENLIBRARY_ENABLED', 'true').lower() == 'true'

# ============ Sync ============
VAULT_SYNC_INTERVAL_MIN = int(os.environ.get('VAULT_SYNC_INTERVAL_MIN', '30'))

# ============ Display ============
DEFAULT_PORT = int(os.environ.get('MNEMO_PORT', '5000'))


def validate():
    """Validate config, return list of warnings."""
    warnings = []
    if LANGUAGE not in SUPPORTED_LANGUAGES:
        warnings.append(f"Language '{LANGUAGE}' not in supported list {SUPPORTED_LANGUAGES}")
    if not BOOKS_DIR.parent.exists():
        warnings.append(f"Data dir does not exist: {DATA_DIR}")
    return warnings


if __name__ == '__main__':
    warnings = validate()
    print(f"Mnemosyne config:")
    print(f"  Data dir:    {DATA_DIR}")
    print(f"  Database:    {DATABASE_URL}")
    print(f"  Language:    {LANGUAGE}")
    print(f"  Vault:       {VAULT_DIR}")
    print(f"  Hermes:      {'enabled' if HERMES_ENABLED else 'disabled'}")
    print(f"  Port:        {DEFAULT_PORT}")
    if warnings:
        print(f"\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
