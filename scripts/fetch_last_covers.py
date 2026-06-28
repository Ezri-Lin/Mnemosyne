"""Last attempt: search Open Library with English title alternatives for remaining books."""
import sys, os, requests
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

config.COVERS_DIR.mkdir(parents=True, exist_ok=True)

session = get_session()
books = session.query(Book).all()

# More creative search terms
SEARCHES = {
    '真需求': [
        '真需求 梁宁', 'Zhen Xu Qiu Liang Ning',
        'Liang Ning', '梁宁 真需求',
    ],
    '俞军产品方法论': [
        '俞军产品方法论', 'Yu Jun Product Methodology',
        '俞军 产品方法论', 'Yu Jun',
    ],
    '认知觉醒': [
        '认知觉醒 周岭', 'Ren Zhi Jue Xing 周岭',
        '周岭 认知觉醒',
    ],
    '认知驱动': [
        '认知驱动 周岭', 'Ren Zhi Qu Dong 周岭',
        '周岭 认知驱动',
    ],
}

found = 0

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    if not cover_path.exists() or cover_path.stat().st_size >= 18000:
        continue
    
    queries = SEARCHES.get(book.title, [book.title])
    
    print(f"{book.title}: ", end='', flush=True)
    
    got = False
    for q in queries:
        try:
            r = requests.get('https://openlibrary.org/search.json',
                             params={'q': q, 'limit': 5}, timeout=10)
            for doc in r.json().get('docs', []):
                cover_id = doc.get('cover_i')
                if cover_id:
                    img = requests.get(f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg', timeout=15)
                    if img.status_code == 200 and len(img.content) > 5000:
                        cover_path.write_bytes(img.content)
                        print(f'✓ {q}')
                        found += 1
                        got = True
                        break
            if got:
                break
        except:
            pass
    
    if not got:
        # Try direct search on Douban HTML
        try:
            r = requests.get(
                'https://book.douban.com/subject_search',
                params={'search_text': book.title},
                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'},
                timeout=10
            )
            if r.status_code == 200:
                html = r.text
                # Find cover images in search results
                import re
                covers = re.findall(r'src="(https://img[^"]+\.jpg)"', html)
                for url in covers[:3]:
                    if 's.jpg' in url:
                        url = url.replace('s.jpg', 'l.jpg')
                    img = requests.get(url, timeout=10)
                    if img.status_code == 200 and len(img.content) > 5000:
                        cover_path.write_bytes(img.content)
                        print('Douban ✓')
                        found += 1
                        got = True
                        break
        except:
            pass
    
    if not got:
        print('✗')

session.close()
print(f'\nGot {found} more covers')
