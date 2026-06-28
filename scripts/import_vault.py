"""Scan the vault directory and seed the DB with all books found."""
import sys, os, json, re
sys.path.insert(0, '/app')
from datetime import datetime
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

session = get_session()
session.query(Book).delete()
session.commit()

vault_books_dir = config.VAULT_BOOKS_DIR
if not vault_books_dir.exists():
    print(f"Vault books dir not found: {vault_books_dir}")
    sys.exit(1)

added = 0
seen_slugs = set()

for src in vault_books_dir.glob('**/source/*'):
    if not src.is_file():
        continue
    item = src.parent.parent
    title = item.name
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", '-', slug).strip('-').lower()
    
    if slug in seen_slugs:
        continue
    seen_slugs.add(slug)
    
    vault_rel = str(item.relative_to(config.VAULT_DIR))
    
    book = Book(
        slug=slug,
        title=title,
        author='Unknown',
        lang='zh' if any('\u4e00' <= c <= '\u9fff' for c in title) else 'en',
        status='to-read',
        tags='[]',
        source_format=src.suffix[1:],
        vault_path=vault_rel,
        added_at=datetime.now().isoformat(),
    )
    session.add(book)
    added += 1

session.commit()
session.close()
print(f"Imported {added} books from vault")
