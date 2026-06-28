"""
Mnemosyne Flask app.
- /              → poster wall (books grid)
- /book/<slug>   → book Architecture page
- /api/books     → JSON book list
- /api/upload    → POST file (EPUB/PDF/MOBI) → trigger analysis
- /api/status    → GET/PUT book status
"""

import os
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='../static', template_folder='../static/templates')
CORS(app)

# ============ Paths ============
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'data'
BOOKS_DIR = DATA_DIR / 'books'
GENERATED_DIR = DATA_DIR / 'generated'
COVERS_DIR = DATA_DIR / 'covers'
DB_PATH = DATA_DIR / 'mnemosyne.db'

# Vault (Golden-House) - synced via git
VAULT_DIR = Path(os.environ.get('VAULT_DIR', '/Users/ezri/Library/Mobile Documents/iCloud~md~obsidian/Documents/Golden House'))
VAULT_BOOKS_DIR = VAULT_DIR / '5.0 Books & Reading' / 'Books'


# ============ Database ============
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create schema if not exists."""
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS books (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                lang TEXT DEFAULT 'en',
                status TEXT DEFAULT 'to-read',  -- to-read, reading, completed, paused, dropped
                rating INTEGER DEFAULT 0,
                year INTEGER,
                tags TEXT,                        -- JSON array
                added_at TEXT,
                source_format TEXT,               -- epub, pdf, mobi, txt
                source_path TEXT,                 -- relative to data/books/
                vault_path TEXT,                  -- absolute path in vault
                notes TEXT,                        -- user's reason for adding
                last_analyzed TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
            CREATE INDEX IF NOT EXISTS idx_books_lang ON books(lang);

            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,                       -- 'vault' or 'upload'
                action TEXT,                       -- 'create', 'update', 'analyze'
                book_slug TEXT,
                status TEXT,                       -- 'ok' or 'error'
                message TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')


# ============ Routes ============

@app.route('/')
def poster_wall():
    """Main page - poster wall."""
    return render_template('poster-wall.html', books=get_all_books_with_vault_status())


@app.route('/book/<slug>/')
def book_page(slug):
    """Book architecture page. If HTML exists in data/generated/, serve it.
    Else redirect to vault or show placeholder."""
    gen_dir = GENERATED_DIR / slug
    if (gen_dir / 'index.html').exists():
        return send_from_directory(gen_dir, 'index.html')
    # Fallback: check vault (synced)
    vault_book = VAULT_BOOKS_DIR / slug
    if (vault_book / 'web' / 'index.html').exists():
        return send_from_directory(vault_book / 'web', 'index.html')
    return f"<h1>Book not yet analyzed: {slug}</h1><p><a href='/'>Back</a></p>"


@app.route('/chapter/<slug>/<chapter>.html')
def chapter_page(slug, chapter):
    """Serve a specific chapter HTML."""
    gen_file = GENERATED_DIR / slug / 'chapters' / chapter
    if gen_file.exists():
        return send_from_directory(gen_file.parent, gen_file.name)
    return "Not found", 404


@app.route('/api/books')
def api_books():
    """JSON list of all books."""
    books = get_all_books_with_vault_status()
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
    lang = request.form.get('lang', 'en')
    status = request.form.get('status', 'to-read')
    notes = request.form.get('notes', '')

    # Generate slug from title + author
    slug = make_slug(title, author)
    ext = file.filename.rsplit('.', 1)[-1].lower()

    # Save file
    book_dir = BOOKS_DIR / slug
    book_dir.mkdir(parents=True, exist_ok=True)
    source_path = book_dir / f"source.{ext}"
    file.save(source_path)

    # Insert/update DB
    with get_db() as conn:
        conn.execute('''
            INSERT INTO books (slug, title, author, lang, status, tags, source_format, source_path, notes, added_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title=excluded.title,
                author=excluded.author,
                updated_at=datetime('now')
        ''', (slug, title, author, lang, status, '[]', ext, str(source_path.relative_to(ROOT)), notes, datetime.now().isoformat()))

    # Trigger analysis (async or sync?)
    # For MVP, sync (simple)
    analyze_book(slug)

    return jsonify({'status': 'ok', 'slug': slug, 'message': f'Book {slug} uploaded and queued for analysis'})


@app.route('/api/status/<slug>', methods=['PUT'])
def api_update_status(slug):
    """Update book status (to-read, reading, completed, paused, dropped)."""
    data = request.json
    new_status = data.get('status')
    rating = data.get('rating')
    if new_status not in ('to-read', 'reading', 'completed', 'paused', 'dropped'):
        return jsonify({'error': 'invalid status'}), 400
    with get_db() as conn:
        if rating is not None:
            conn.execute('UPDATE books SET status=?, rating=?, updated_at=datetime(\'now\') WHERE slug=?', (new_status, rating, slug))
        else:
            conn.execute('UPDATE books SET status=?, updated_at=datetime(\'now\') WHERE slug=?', (new_status, slug))
    return jsonify({'status': 'ok'})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '0.1.0'})


# ============ Helpers ============

def make_slug(title, author):
    import re
    s = (title + ' ' + author).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def get_all_books_with_vault_status():
    """Read books from DB, merge with vault frontmatter if available."""
    books = []
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    for row in rows:
        b = dict(row)
        # Try to get cover/icon from vault (if synced)
        # TODO: pull from vault frontmatter
        books.append(b)
    return books


def analyze_book(slug):
    """
    Convert source file → TXT, extract chapters, render HTML.
    Uses scripts from analyzer/.
    """
    book_dir = BOOKS_DIR / slug
    source_path = next(iter(book_dir.glob('source.*')), None)
    if not source_path:
        return False

    ext = source_path.suffix.lstrip('.')

    # Step 1: convert to TXT
    txt_path = book_dir / 'source.txt'
    if ext == 'txt':
        # already text
        import shutil
        shutil.copy(source_path, txt_path)
    elif ext == 'epub':
        subprocess.run(['ebook-convert', str(source_path), str(txt_path)], check=True)
    elif ext in ('pdf',):
        subprocess.run(['pdftotext', str(source_path), str(txt_path)], check=True)
    # TODO: mobi, azw, etc.

    # Step 2: extract chapters + render HTML
    # TODO: implement chapter extraction
    # For now, placeholder
    gen_dir = GENERATED_DIR / slug
    gen_dir.mkdir(parents=True, exist_ok=True)
    (gen_dir / 'README.txt').write_text(f"Analysis pending for {slug}. Source: {txt_path}")

    # Update DB
    with get_db() as conn:
        conn.execute('UPDATE books SET last_analyzed=datetime(\'now\') WHERE slug=?', (slug,))
    return True


# ============ Main ============
if __name__ == '__main__':
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
