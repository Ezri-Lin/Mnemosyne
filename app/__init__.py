"""
Mnemosyne Flask app.
- /              → poster wall (books grid)
- /book/<slug>   → book Architecture page
- /api/books     → JSON book list
- /api/upload    → POST file (EPUB/PDF/MOBI) → trigger analysis
- /api/status    → GET/PUT book status
- /health        → liveness probe
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, send_from_directory, g
from flask_cors import CORS

from app import config

app = Flask(__name__, static_folder='../static', template_folder='../static/templates')
CORS(app)

# ============ Per-request language ============
@app.before_request
def set_language():
    """Language can be overridden per-request via ?lang=zh or Accept-Language header."""
    req_lang = request.args.get('lang')
    if not req_lang:
        # Parse from Accept-Language
        accept = request.headers.get('Accept-Language', '')
        for part in accept.split(','):
            code = part.split(';')[0].strip().lower()[:2]
            if code in config.SUPPORTED_LANGUAGES:
                req_lang = code
                break
    g.lang = req_lang if req_lang in config.SUPPORTED_LANGUAGES else config.LANGUAGE

@app.context_processor
def inject_globals():
    return {
        'lang': g.get('lang', config.LANGUAGE),
        'default_lang': config.LANGUAGE,
        'supported_languages': config.SUPPORTED_LANGUAGES,
    }


# ============ Database (with DATABASE_URL support) ============
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    slug = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    lang = Column(String, default='en')
    status = Column(String, default='to-read')  # to-read, reading, completed, paused, dropped
    rating = Column(Integer, default=0)
    year = Column(Integer)
    tags = Column(Text)  # JSON array
    added_at = Column(String)
    source_format = Column(String)  # epub, pdf, mobi, txt
    source_path = Column(String)
    vault_path = Column(String)
    notes = Column(Text)
    last_analyzed = Column(String)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())


class SyncLog(Base):
    __tablename__ = 'sync_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)  # 'vault' or 'upload'
    action = Column(String)  # 'create', 'update', 'analyze'
    book_slug = Column(String)
    status = Column(String)  # 'ok' or 'error'
    message = Column(Text)
    created_at = Column(String, default=lambda: datetime.now().isoformat())


def get_engine():
    """Create SQLAlchemy engine from DATABASE_URL."""
    url = config.DATABASE_URL
    if url.startswith('sqlite:///'):
        # Ensure SQLite file path is absolute
        path = url.replace('sqlite:///', '')
        if not os.path.isabs(path):
            path = str(config.ROOT / path)
        url = f'sqlite:///{path}'
    return create_engine(url, echo=False)


engine = get_engine()
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False))
Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()


# ============ Routes ============

@app.route('/')
def poster_wall():
    """Main page - poster wall."""
    return render_template('poster-wall.html', books=get_all_books())


@app.route('/book/<slug>/')
def book_page(slug):
    """Book architecture page. If HTML exists in data/generated/, serve it.
    Else redirect to vault or show placeholder."""
    gen_dir = config.GENERATED_DIR / slug
    if (gen_dir / 'index.html').exists():
        return send_from_directory(gen_dir, 'index.html')
    # Fallback: check vault (synced)
    vault_book = config.VAULT_BOOKS_DIR / slug
    if (vault_book / 'web' / 'index.html').exists():
        return send_from_directory(vault_book / 'web', 'index.html')
    return f"<h1>Book not yet analyzed: {slug}</h1><p><a href='/'>Back</a></p>"


@app.route('/chapter/<slug>/<chapter>.html')
def chapter_page(slug, chapter):
    """Serve a specific chapter HTML."""
    gen_file = config.GENERATED_DIR / slug / 'chapters' / chapter
    if gen_file.exists():
        return send_from_directory(gen_file.parent, gen_file.name)
    return "Not found", 404


@app.route('/api/books')
def api_books():
    """JSON list of all books."""
    books = get_all_books()
    return jsonify(books)


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    POST file (multipart) + metadata.
    1. Save to data/books/<slug>/source.<ext>
    2. Run analyzer (convert + extract chapters + render HTML)
    3. Update DB
    """
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    file = request.files['file']
    title = request.form.get('title', file.filename.rsplit('.', 1)[0])
    author = request.form.get('author', 'Unknown')
    lang = request.form.get('lang', config.LANGUAGE)
    status = request.form.get('status', 'to-read')
    notes = request.form.get('notes', '')

    # Generate slug from title + author
    slug = make_slug(title, author)
    ext = file.filename.rsplit('.', 1)[-1].lower()

    # Save file
    book_dir = config.BOOKS_DIR / slug
    book_dir.mkdir(parents=True, exist_ok=True)
    source_path = book_dir / f"source.{ext}"
    file.save(source_path)

    # Insert/update DB
    session = get_session()
    book = session.query(Book).filter_by(slug=slug).first()
    if book is None:
        book = Book(
            slug=slug,
            title=title,
            author=author,
            lang=lang,
            status=status,
            tags='[]',
            source_format=ext,
            source_path=str(source_path.relative_to(config.ROOT)),
            notes=notes,
            added_at=datetime.now().isoformat(),
        )
        session.add(book)
    else:
        book.title = title
        book.author = author
        book.updated_at = datetime.now().isoformat()
    session.commit()

    # Trigger analysis (MVP: sync)
    analyze_book(slug)
    session.close()

    return jsonify({'status': 'ok', 'slug': slug, 'message': f'Book {slug} uploaded'})


@app.route('/api/status/<slug>', methods=['PUT'])
def api_update_status(slug):
    """Update book status (to-read, reading, completed, paused, dropped)."""
    data = request.json
    new_status = data.get('status')
    rating = data.get('rating')
    if new_status not in ('to-read', 'reading', 'completed', 'paused', 'dropped'):
        return jsonify({'error': 'invalid status'}), 400
    session = get_session()
    book = session.query(Book).filter_by(slug=slug).first()
    if not book:
        return jsonify({'error': 'not found'}), 404
    book.status = new_status
    if rating is not None:
        book.rating = rating
    book.updated_at = datetime.now().isoformat()
    session.commit()
    session.close()
    return jsonify({'status': 'ok'})


@app.route('/api/config')
def api_config():
    """Expose non-sensitive config (for frontend)."""
    return jsonify({
        'language': config.LANGUAGE,
        'default_lang': config.LANGUAGE,
        'supported_languages': config.SUPPORTED_LANGUAGES,
        'hermes_enabled': config.HERMES_ENABLED,
        'vault_dir': str(config.VAULT_DIR),
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '0.1.0'})


# ============ Helpers ============

def make_slug(title, author):
    import re
    s = (title + ' ' + author).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def get_all_books():
    """Read all books from DB."""
    session = get_session()
    books = []
    for b in session.query(Book).order_by(Book.title).all():
        books.append({
            'slug': b.slug,
            'title': b.title,
            'author': b.author,
            'lang': b.lang,
            'status': b.status,
            'rating': b.rating or 0,
            'year': b.year,
            'tags': json.loads(b.tags) if b.tags else [],
            'added_at': b.added_at,
            'notes': b.notes,
        })
    session.close()
    return books


def analyze_book(slug):
    """
    Convert source file → TXT, extract chapters, render HTML.
    """
    book_dir = config.BOOKS_DIR / slug
    source_path = next(iter(book_dir.glob('source.*')), None)
    if not source_path:
        return False

    ext = source_path.suffix.lstrip('.')

    # Step 1: convert to TXT
    txt_path = book_dir / 'source.txt'
    if ext == 'txt':
        import shutil
        shutil.copy(source_path, txt_path)
    elif ext == 'epub':
        subprocess.run(['ebook-convert', str(source_path), str(txt_path)], check=True)
    elif ext in ('pdf',):
        subprocess.run(['pdftotext', str(source_path), str(txt_path)], check=True)
    # TODO: mobi, azw, etc.

    # Step 2: extract chapters + render HTML
    # TODO: implement chapter extraction
    gen_dir = config.GENERATED_DIR / slug
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / 'README.txt').write_text(f"Analysis pending for {slug}. Source: {txt_path}")

    # Update DB
    session = get_session()
    book = session.query(Book).filter_by(slug=slug).first()
    if book:
        book.last_analyzed = datetime.now().isoformat()
        book.updated_at = datetime.now().isoformat()
        session.commit()
    session.close()
    return True


# ============ Main ============
if __name__ == '__main__':
    config.BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    config.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    config.COVERS_DIR.mkdir(parents=True, exist_ok=True)
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    warnings = config.validate()
    if warnings:
        print("Config warnings:")
        for w in warnings:
            print(f"  - {w}")
    app.run(debug=True, host='0.0.0.0', port=config.DEFAULT_PORT)
