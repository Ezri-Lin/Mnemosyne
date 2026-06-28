"""Seed the database with test books for local development."""
import sys
sys.path.insert(0, '.')
from app import get_session, Book
from datetime import datetime

session = get_session()

# Clear existing books
session.query(Book).delete()
session.commit()

# Seed data (matching your vault's poster wall demo)
books = [
    {"slug": "the-body-keeps-the-score", "title": "The Body Keeps the Score", "author": "Bessel van der Kolk", "lang": "en", "status": "reading", "year": 2014, "tags": '["trauma","neuroscience"]'},
    {"slug": "atomic-habits", "title": "Atomic Habits", "author": "James Clear", "lang": "en", "status": "completed", "rating": 5, "year": 2018, "tags": '["productivity","habits"]'},
    {"slug": "thinking-fast-and-slow", "title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "lang": "en", "status": "completed", "rating": 5, "year": 2011, "tags": '["psychology","decision-making"]'},
    {"slug": "antifragile", "title": "Antifragile", "author": "Nassim Taleb", "lang": "en", "status": "reading", "year": 2012, "tags": '["philosophy","risk"]'},
    {"slug": "influence", "title": "Influence", "author": "Robert Cialdini", "lang": "en", "status": "to-read", "year": 1984, "tags": '["psychology","marketing"]'},
    {"slug": "sapiens", "title": "Sapiens", "author": "Yuval Noah Harari", "lang": "en", "status": "completed", "rating": 4, "year": 2014, "tags": '["history","philosophy"]'},
    {"slug": "deep-work", "title": "Deep Work", "author": "Cal Newport", "lang": "en", "status": "to-read", "year": 2016, "tags": '["productivity","focus"]'},
    {"slug": "man-search-meaning", "title": "Man's Search for Meaning", "author": "Viktor Frankl", "lang": "en", "status": "completed", "rating": 5, "year": 1946, "tags": '["psychology","philosophy"]'},
]

for b in books:
    book = Book(**b, added_at=datetime.now().isoformat())
    session.add(book)

session.commit()
session.close()
print(f"Seeded {len(books)} books. Access at http://localhost:5050/")
