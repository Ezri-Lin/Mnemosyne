"""Fetch real cover images from Google Books API for placeholder covers."""
import sys, os, requests
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

config.COVERS_DIR.mkdir(parents=True, exist_ok=True)

session = get_session()
books = session.query(Book).all()

# Books with placeholder covers (small file = no real cover from Open Library)
SEARCH_QUERIES = {
    '23-anti-procrastination-habits': '23 Anti-Procrastination Habits',
    'the-e-myth-revisited': 'The E Myth Revisited Michael Gerber',
    '经济学的思维方式': '经济学的思维方式 托马斯·索维尔',
    '财富自由之路': '财富自由之路 李笑来',
    '俞军产品方法论': '俞军产品方法论',
    '华与华方法': '华与华方法 华杉',
    '真需求': '真需求 梁宁',
    '营销的终结': '营销的终结 卡洛斯·吉尔',
    '认知觉醒': '认知觉醒 周岭',
    '认知驱动': '认知驱动 周岭',
}

found = 0

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    if not cover_path.exists():
        continue
    
    # Check if it's a placeholder (small file < 18KB)
    if cover_path.stat().st_size >= 18000:
        continue
    
    q = SEARCH_QUERIES.get(book.slug) or SEARCH_QUERIES.get(book.title)
    if not q:
        continue
    
    print(f"Searching: {q}", end='')
    try:
        r = requests.get(
            'https://www.googleapis.com/books/v1/volumes',
            params={'q': q, 'maxResults': 5, 'langRestrict': 'zh' if any('\u4e00' <= c <= '\u9fff' for c in q) else 'en'},
            timeout=15
        )
        data = r.json()
        items = data.get('items', [])
        for item in items:
            info = item.get('volumeInfo', {})
            image_links = info.get('imageLinks', {})
            img_url = image_links.get('extraLarge') or image_links.get('large') or image_links.get('medium') or image_links.get('thumbnail')
            if img_url:
                # Fix http -> https
                img_url = img_url.replace('http://', 'https://')
                # Remove zoom parameter
                img_url = img_url.split('&')[0]
                img = requests.get(img_url, timeout=15)
                if img.status_code == 200:
                    cover_path.write_bytes(img.content)
                    print(f' → cover ✓ ({len(img.content)} bytes)')
                    found += 1
                    break
        else:
            print(' → no cover in Google Books')
    except Exception as e:
        print(f' → error: {e}')

session.close()
print(f'\nUpdated {found} covers')
