"""Fill remaining missing metadata from book content + Google Books API."""
import sys, os, re, json, requests
sys.path.insert(0, '/app')
from datetime import datetime
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config

session = get_session()

# Manual overrides for books we can identify from content
MANUAL = {
    '经济学的思维方式': {
        'author': '托马斯·索维尔 (Thomas Sowell)',
        'year': 2015,
        'search': 'Basic Economics Thomas Sowell'
    },
    '营销的终结': {
        'author': '卡洛斯·吉尔 (Carlos Gil)',
        'year': 2020,
        'search': 'The End of Marketing Carlos Gil'
    },
    '认知觉醒': {
        'author': '周岭',
        'year': 2020,
        'search': '认知觉醒 周岭'
    },
    '财富自由之路': {
        'author': '李笑来',
        'year': 2017,
        'search': '财富自由之路 李笑来'
    },
    '真需求': {
        'author': '梁宁',
        'year': 2024,
        'search': '真需求 梁宁'
    },
    '俞军产品方法论': {
        'author': '俞军',
        'year': 2019,
        'search': '俞军产品方法论'
    },
    '华与华方法': {
        'author': '华杉、华楠',
        'year': 2019,
        'search': '华与华方法 华杉'
    },
}

updated = 0
for book in session.query(Book).all():
    if book.author != 'Unknown' and book.year:
        continue

    manual = MANUAL.get(book.title)
    if not manual:
        continue

    changed = False
    if book.author == 'Unknown' and manual.get('author'):
        book.author = manual['author']
        changed = True
    if not book.year and manual.get('year'):
        book.year = manual['year']
        changed = True

    if changed:
        book.updated_at = datetime.now().isoformat()
        updated += 1
        print(f"{'✓' if book.author != 'Unknown' else ' '} {'✓' if book.year else ' '} {book.title}: {book.author} ({book.year})")

session.commit()
session.close()
print(f"\nUpdated {updated} books")
