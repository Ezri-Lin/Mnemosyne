"""Enrich book metadata from vault markdown frontmatter + Open Library API."""
import sys, os, json, re, requests
sys.path.insert(0, '/app')
from datetime import datetime
from pathlib import Path
import yaml
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

session = get_session()
books = session.query(Book).all()
updated = 0

def parse_frontmatter(path):
    """Parse YAML frontmatter from a markdown file."""
    if not path or not path.exists():
        return {}
    text = path.read_text(encoding='utf-8', errors='replace')
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if m:
        try:
            return yaml.safe_load(m.group(1)) or {}
        except:
            return {}
    return {}

def fetch_openlibrary(title, author):
    """Search Open Library for book metadata."""
    q = title
    if author and author != 'Unknown':
        q += f' {author}'
    try:
        r = requests.get('https://openlibrary.org/search.json', params={'q': q, 'limit': 3}, timeout=10)
        data = r.json()
        docs = data.get('docs', [])
        for doc in docs:
            ol_title = doc.get('title', '')
            ol_author = ', '.join(doc.get('author_name', [])) if doc.get('author_name') else ''
            ol_year = doc.get('first_publish_year')
            ol_lang = doc.get('language', [])
            ol_cover = doc.get('cover_i')
            return {
                'author': ol_author or None,
                'year': ol_year,
                'lang': ol_lang[0] if ol_lang and ol_lang[0] in ('en', 'zh', 'ja', 'es', 'fr', 'de') else None,
                'cover_id': ol_cover,
            }
    except:
        return {}
    return {}

def download_cover(cover_id, slug):
    """Download cover from Open Library."""
    if not cover_id:
        return False
    cover_path = config.COVERS_DIR / f"{slug}.jpg"
    if cover_path.exists():
        return True
    try:
        r = requests.get(f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg', timeout=15)
        if r.status_code == 200:
            cover_path.write_bytes(r.content)
            return True
    except:
        pass
    return False

for book in books:
    changed = False
    
    # Find markdown file in vault
    vault_rel = book.vault_path or ''
    if not vault_rel:
        continue
    
    md_path = config.VAULT_DIR / vault_rel / f"{book.title}.md"
    if not md_path.exists():
        # Try alternative filenames
        for f in (config.VAULT_DIR / vault_rel).glob('*.md'):
            md_path = f
            break
    
    fm = parse_frontmatter(md_path) if md_path.exists() else {}
    
    # Update from frontmatter
    if fm.get('author') and book.author == 'Unknown':
        book.author = fm['author']
        changed = True
    if fm.get('year') and not book.year:
        book.year = int(fm['year']) if str(fm['year']).isdigit() else None
        changed = True
    if fm.get('language') and book.lang == 'en':
        book.lang = fm['language']
        changed = True
    
    # Fallback to Open Library
    if book.author == 'Unknown' or not book.year or not book.lang:
        meta = fetch_openlibrary(book.title, book.author if book.author != 'Unknown' else '')
        if meta:
            if book.author == 'Unknown' and meta.get('author'):
                book.author = meta['author']
                changed = True
            if not book.year and meta.get('year'):
                book.year = meta['year']
                changed = True
            if book.lang == 'en' and meta.get('lang'):
                book.lang = meta['lang']
                changed = True
            if not config.COVERS_DIR.exists():
                config.COVERS_DIR.mkdir(parents=True)
            if meta.get('cover_id'):
                download_cover(meta['cover_id'], book.slug)
    
    if changed:
        book.updated_at = datetime.now().isoformat()
        updated += 1
        print(f"  ✓ {book.title}: author={book.author}, year={book.year}, lang={book.lang}")

session.commit()
session.close()
print(f"\nUpdated {updated} books")
print(f"Covers dir: {config.COVERS_DIR}")
print(f"Covers: {list(config.COVERS_DIR.glob('*.jpg'))}")
