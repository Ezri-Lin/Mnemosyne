"""Fetch covers using multiple APIs."""
import sys, os, requests, re
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

config.COVERS_DIR.mkdir(parents=True, exist_ok=True)

session = get_session()
books = session.query(Book).all()

# Alternative search queries for Open Library
ALT_SEARCHES = {
    '23-anti-procrastination-habits': ['23 Anti-Procrastination Habits', 'Anti Procrastination Habits Scott'],
    'the-e-myth-revisited': ['The E-Myth Revisited', 'E Myth Revisited'],
    '经济学的思维方式': ['Basic Economics Thomas Sowell', 'Basic Economics', '经济学的思维方式'],
    '财富自由之路': ['财富自由之路', 'Road to Financial Freedom'],
    '俞军产品方法论': ['俞军产品方法论', 'Yu Jun Product Methodology'],
    '华与华方法': ['华与华方法', 'Hua Shan Hua Nan Method'],
    '真需求': ['真需求', 'Liang Ning Zhen Xu Qiu'],
    '营销的终结': ['The End of Marketing Carlos Gil', '营销的终结'],
    '认知觉醒': ['认知觉醒', '周岭 认知觉醒'],
    '认知驱动': ['认知驱动', '周岭 认知驱动'],
}

found = 0

def try_openlibrary(q):
    try:
        r = requests.get('https://openlibrary.org/search.json',
                         params={'q': q, 'limit': 10}, timeout=10)
        for doc in r.json().get('docs', []):
            cover_id = doc.get('cover_i')
            if cover_id:
                img = requests.get(f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg', timeout=15)
                if img.status_code == 200 and len(img.content) > 5000:
                    return img.content
    except:
        pass
    return None

def try_douban(title, author):
    """Try Douban book search API."""
    q = title
    if author and author != 'Unknown':
        q += ' ' + author
    try:
        # Douban API v2 (public, rate-limited)
        r = requests.get('https://api.douban.com/v2/book/search',
                         params={'q': q, 'count': 5}, 
                         headers={'User-Agent': 'Mozilla/5.0'},
                         timeout=10)
        data = r.json()
        for book_data in data.get('books', []):
            img_url = book_data.get('images', {}).get('large')
            if img_url:
                img = requests.get(img_url, timeout=15)
                if img.status_code == 200 and len(img.content) > 5000:
                    return img.content
    except:
        pass
    return None

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    if not cover_path.exists():
        continue
    
    # Skip if already has a real cover (>18KB)
    if cover_path.stat().st_size >= 18000:
        continue
    
    queries = ALT_SEARCHES.get(book.slug) or ALT_SEARCHES.get(book.title, [book.title])
    
    print(f"{book.title}: ", end='', flush=True)
    
    # Try Douban first for Chinese books
    img_data = None
    if any('\u4e00' <= c <= '\u9fff' for c in book.title):
        img_data = try_douban(book.title, book.author)
        if img_data:
            print('Douban ✓')
    
    # Try Open Library with various queries
    if not img_data:
        for q in queries:
            img_data = try_openlibrary(q)
            if img_data:
                print(f'OL({q[:30]}) ✓')
                break
    
    if img_data:
        cover_path.write_bytes(img_data)
        found += 1
    else:
        print('still no cover')

session.close()
print(f'\nUpdated {found} covers')
