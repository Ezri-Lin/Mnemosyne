"""Fetch metadata for remaining books without author/year."""
import sys, os, requests
sys.path.insert(0, '/app')
from datetime import datetime
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

session = get_session()
books = session.query(Book).all()
updated = 0

for book in books:
    if book.author != 'Unknown' and book.year:
        continue  
    
    q = book.title
    # Remove subtitle after colon/dash
    q = q.split(':')[0].split('—')[0].strip()
    if 'zh' in book.lang or any('\u4e00' <= c <= '\u9fff' for c in book.title):
        q = book.title
    
    print(f"Looking up: {book.title}", end='')
    try:
        r = requests.get('https://openlibrary.org/search.json',
                         params={'q': q, 'limit': 5}, timeout=10)
        docs = r.json().get('docs', [])
        for doc in docs:
            author = ', '.join(doc.get('author_name', [])) if doc.get('author_name') else ''
            year = doc.get('first_publish_year')
            if book.author == 'Unknown' and author:
                book.author = author
            if not book.year and year:
                book.year = year
            break
    except:
        pass
    
    if book.author != 'Unknown' or book.year:
        book.updated_at = datetime.now().isoformat()
        updated += 1
        print(f' → author={book.author}, year={book.year}')
    else:
        print(' → still not found')

session.commit()
session.close()
print(f'\nUpdated {updated} books')
