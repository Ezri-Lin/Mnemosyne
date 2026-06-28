"""Fetch covers for books missing them, using Open Library API."""
import sys, os, requests
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

session = get_session()
books = session.query(Book).all()

config.COVERS_DIR.mkdir(parents=True, exist_ok=True)
found = 0

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    if cover_path.exists():
        continue
    
    q = book.title
    if book.author and book.author != 'Unknown':
        q += ' ' + book.author.split(',')[0].split('&')[0].strip()
    
    print(f"Searching: {q}", end='')
    try:
        r = requests.get('https://openlibrary.org/search.json', params={'q': q, 'limit': 5}, timeout=10)
        docs = r.json().get('docs', [])
        for doc in docs:
            cover_id = doc.get('cover_i')
            if cover_id:
                img = requests.get(f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg', timeout=15)
                if img.status_code == 200:
                    cover_path.write_bytes(img.content)
                    print(f' → cover {cover_id} ✓')
                    found += 1
                    break
        else:
            print(' → no cover found')
    except Exception as e:
        print(f' → error: {e}')

session.close()
print(f'\nDownloaded {found} new covers')
