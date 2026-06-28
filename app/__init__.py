"""
Mnemosyne — display layer for book analysis.
- /              → poster wall (books grid)
- /book/<slug>   → book Architecture page (serves vault web/index.html)
- /api/books     → JSON book list
- /api/upload    → POST file (EPUB/PDF)
- /api/status    → GET/PUT book status
- /health        → liveness probe

NOTE: AI analysis no longer happens here. All analysis is done by an AI Agent
that can load the book-analyst skill. Mnemosyne only stores, displays, and
serves the results.
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
    status = Column(String, default='to-read')
    rating = Column(Integer, default=0)
    year = Column(Integer)
    tags = Column(Text)
    added_at = Column(String)
    source_format = Column(String)
    source_path = Column(String)
    vault_path = Column(String)
    notes = Column(Text)
    last_analyzed = Column(String)
    created_at = Column(String, default=lambda: datetime.now().isoformat())
    updated_at = Column(String, default=lambda: datetime.now().isoformat())


class SyncLog(Base):
    __tablename__ = 'sync_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)
    action = Column(String)
    book_slug = Column(String)
    status = Column(String)
    message = Column(Text)
    created_at = Column(String, default=lambda: datetime.now().isoformat())


def get_engine():
    url = config.DATABASE_URL
    if url.startswith('sqlite:///'):
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


# ============ Helpers ============

def make_slug(title, author=None):
    """Generate URL-safe slug from title."""
    import re
    s = title if author is None else f'{title}-{author}'
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', s)
    return s.strip('-')


def get_all_books():
    """Return all books as list of dicts."""
    session = get_session()
    books = session.query(Book).order_by(Book.added_at.desc()).all()
    result = []
    for b in books:
        data = {
            'slug': b.slug,
            'title': b.title or b.slug,
            'author': b.author or '',
            'lang': b.lang or 'en',
            'status': b.status or 'to-read',
            'rating': b.rating or 0,
            'year': b.year,
            'tags': json.loads(b.tags) if b.tags else [],
            'added_at': b.added_at or '',
            'last_analyzed': b.last_analyzed or '',
            'source_format': b.source_format or '',
            'notes': b.notes or '',
            'parse_status': 'parsed' if b.last_analyzed else 'not-parsed',
        }
        # Check for web/index.html in vault
        if config.VAULT_DIR and config.VAULT_BOOKS_DIR:
            for folder in config.VAULT_BOOKS_DIR.iterdir():
                if not folder.is_dir():
                    continue
                folder_slug = make_slug(folder.name)
                if folder_slug == b.slug and (folder / 'web' / 'index.html').exists():
                    data['parse_status'] = 'parsed'
                    break
        result.append(data)
    session.close()
    return result


def find_source(slug):
    """Find source file for a book. Checks vault first, then local BOOKS_DIR."""
    # Vault: 5.0 Books & Reading/Books/<slug>/source/
    if config.VAULT_DIR and config.VAULT_BOOKS_DIR:
        for folder in config.VAULT_BOOKS_DIR.iterdir():
            if not folder.is_dir():
                continue
            folder_slug = make_slug(folder.name)
            if folder_slug == slug:
                src_dir = folder / 'source'
                if src_dir.exists():
                    for f in sorted(src_dir.iterdir()):
                        if f.suffix.lower() in ('.txt', '.md', '.epub', '.pdf'):
                            return f, 'vault'
                break  # Found folder but no source

    # Local: data/books/<slug>/
    local = config.BOOKS_DIR / slug
    if local.exists():
        for f in sorted(local.iterdir()):
            if f.suffix.lower() in ('.txt', '.md', '.epub', '.pdf'):
                return f, 'local'
    return None, None


# ============ No-Cache ============

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# ============ Routes ============

@app.route('/')
def poster_wall():
    return render_template('poster-wall.html', books=get_all_books())


@app.route('/api/books/<slug>', methods=['DELETE'])
def api_delete_book(slug):
    import shutil
    session = get_session()
    book = session.query(Book).filter_by(slug=slug).first()
    if not book:
        session.close()
        return jsonify({'error': 'not found'}), 404
    session.delete(book)
    session.commit()
    session.close()
    for d in [config.BOOKS_DIR / slug, config.GENERATED_DIR / slug]:
        if d.exists():
            shutil.rmtree(d)
    return jsonify({'status': 'ok'})


def _find_vault_folder(slug):
    """Find vault folder matching slug (case-insensitive, slug-normalized)."""
    import re as _re
    if not config.VAULT_BOOKS_DIR or not config.VAULT_BOOKS_DIR.exists():
        return None
    for folder in config.VAULT_BOOKS_DIR.iterdir():
        if not folder.is_dir():
            continue
        folder_slug = _re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', folder.name.lower()).strip('-')
        if folder_slug == slug:
            return folder
    return None


@app.route('/book/<slug>/')
def book_page(slug):
    """Serve book Architecture page from vault web/ directory."""
    # First check generated dir
    gen_index = config.GENERATED_DIR / slug / 'index.html'
    if gen_index.exists():
        return send_from_directory(gen_index.parent, 'index.html')

    # Then check vault
    folder = _find_vault_folder(slug)
    if folder:
        web_index = folder / 'web' / 'index.html'
        if web_index.exists():
            return send_from_directory(web_index.parent, 'index.html')

    # No parsed content → show unparsed template
    session = get_session()
    book = session.query(Book).filter_by(slug=slug).first()
    session.close()
    if book:
        return render_template('book-unparsed.html', slug=slug, book_title=book.title or slug)
    return jsonify({'error': 'not found'}), 404


@app.route('/book/<slug>/<path:subpath>')
def book_subpath(slug, subpath):
    """Serve static files (CSS, JS, chapters/*.html) from vault web/."""
    # Check generated dir
    gen_file = config.GENERATED_DIR / slug / subpath
    if gen_file.exists() and gen_file.is_file():
        return send_from_directory(gen_file.parent, gen_file.name)

    # Check vault
    folder = _find_vault_folder(slug)
    if folder:
        vault_file = folder / 'web' / subpath
        if vault_file.exists():
            return send_from_directory(vault_file.parent, vault_file.name)

    return jsonify({'error': 'not found'}), 404


@app.route('/api/books')
def api_books():
    books = get_all_books()
    return jsonify(books)


@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    file = request.files['file']
    title = request.form.get('title', file.filename.rsplit('.', 1)[0])
    author = request.form.get('author', 'Unknown')
    lang = request.form.get('lang', config.LANGUAGE)
    status = request.form.get('status', 'to-read')
    slug = make_slug(title, author)
    ext = file.filename.rsplit('.', 1)[-1].lower()

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}') as tmp:
            file.save(tmp)
            tmp_path = tmp.name

        vault_dir = config.VAULT_BOOKS_DIR / slug / 'source'
        local_dir = config.BOOKS_DIR / slug
        try:
            vault_dir.mkdir(parents=True, exist_ok=True)
            source_path = vault_dir / f"{slug}.{ext}"
            import shutil
            shutil.copy(tmp_path, source_path)
            vault_path = str((config.VAULT_BOOKS_DIR / slug).relative_to(config.VAULT_DIR))
        except (OSError, PermissionError):
            local_dir.mkdir(parents=True, exist_ok=True)
            source_path = local_dir / f"source.{ext}"
            shutil.copy(tmp_path, source_path)
            vault_path = ''
        os.unlink(tmp_path)

        auto_title, auto_author, auto_year, auto_lang = title, author, None, lang
        if ext == 'epub':
            epub_meta = extract_epub_metadata(source_path)
            if epub_meta.get('title'):
                auto_title = epub_meta['title']
            if epub_meta.get('author'):
                auto_author = epub_meta['author']
            if epub_meta.get('year'):
                auto_year = epub_meta['year']
            if epub_meta.get('lang'):
                auto_lang = epub_meta['lang']
            if epub_meta.get('cover_path'):
                import shutil
                cover_dest = config.COVERS_DIR / f"{slug}.jpg"
                shutil.copy(epub_meta['cover_path'], cover_dest)

        session = get_session()
        book = session.query(Book).filter_by(slug=slug).first()
        if book is None:
            book = Book(
                slug=slug,
                title=auto_title,
                author=auto_author,
                lang=auto_lang,
                status=status,
                tags='[]',
                year=auto_year,
                source_format=ext,
                vault_path=vault_path or str(source_path.relative_to(config.ROOT)),
                notes='',
                added_at=datetime.now().isoformat(),
            )
            session.add(book)
        else:
            book.title = auto_title
            book.author = auto_author
            book.updated_at = datetime.now().isoformat()
        session.commit()
        session.close()

        return jsonify({'status': 'ok', 'slug': slug, 'message': f'Book {slug} uploaded'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            session.close()
        except Exception:
            pass
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/status/<slug>', methods=['PUT'])
def api_update_status(slug):
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
    return jsonify({
        'language': config.LANGUAGE,
        'default_lang': config.LANGUAGE,
        'supported_languages': config.SUPPORTED_LANGUAGES,
        'hermes_enabled': config.HERMES_ENABLED,
        'vault_dir': str(config.VAULT_DIR),
    })


@app.route('/api/preview', methods=['POST'])
def api_preview():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[-1].lower()
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix='.' + ext, delete=False)
    tmp.close()
    file.save(tmp.name)
    meta = {'title': '', 'author': '', 'year': None, 'lang': 'en'}
    if ext == 'epub':
        epub_meta = extract_epub_metadata(tmp.name)
        if epub_meta:
            meta.update({k: v for k, v in epub_meta.items() if v})
    try:
        os.unlink(tmp.name)
    except Exception:
        pass
    return jsonify({'status': 'ok', 'metadata': meta})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'version': '0.2.0', 'mode': 'display-only'})


# ============ EPUB Metadata Extraction ============

def extract_epub_metadata(filepath):
    """Extract title, author, year, language, cover from EPUB. 4-level cover fallback."""
    import re as _re
    metadata = {}
    try:
        from ebooklib import epub
        from bs4 import BeautifulSoup
        book = epub.read_epub(str(filepath))

        for ns_key, fields in book.metadata.items():
            for name, values in fields.items():
                if not values:
                    continue
                val_tuple = values[0]
                value_str = str(val_tuple[0]) if val_tuple else ''
                name_lower = name.lower().split(':')[-1]
                if name_lower == 'title':
                    metadata['title'] = value_str
                elif name_lower == 'creator':
                    metadata['author'] = value_str
                elif name_lower == 'date':
                    year_match = _re.search(r'\d{4}', value_str)
                    if year_match:
                        metadata['year'] = int(year_match.group(0))
                elif name_lower == 'language':
                    metadata['lang'] = value_str[:2].lower()

        # Cover: 4 strategies
        try:
            cover_id = None
            opf_ns = 'http://www.idpf.org/2007/opf'
            if opf_ns in book.metadata:
                for name, values in book.metadata[opf_ns].items():
                    if name == 'meta':
                        for val in values:
                            v, attrs = (val[0], val[1]) if isinstance(val, tuple) else (val, {})
                            if attrs.get('name') == 'cover' and attrs.get('content'):
                                cover_id = attrs['content']
                                break
                    if cover_id:
                        break
            if not cover_id:
                for item in book.get_items():
                    if (item.get_id() or '').lower() == 'cover-image':
                        cover_id = item.get_id()
                        break
            if not cover_id:
                for item in book.get_items():
                    n = (item.get_name() or '').lower()
                    i = (item.get_id() or '').lower()
                    if 'cover' in i or 'cover' in n:
                        cover_id = item.get_id()
                        break
            if not cover_id:
                try:
                    import zipfile
                    zf = zipfile.ZipFile(str(filepath), 'r')
                    container = BeautifulSoup(zf.read('META-INF/container.xml'), 'xml')
                    opf_path = None
                    for rf in container.find_all('rootfile'):
                        opf_path = rf.get('full-path')
                        break
                    if opf_path:
                        opf_xml = BeautifulSoup(zf.read(opf_path), 'xml')
                        spine = opf_xml.find('spine') or opf_xml.find('opf:spine')
                        if spine:
                            refs = spine.find_all('itemref') or spine.find_all('opf:itemref')
                            if refs:
                                first_id = refs[0].get('idref')
                                manifest = opf_xml.find('manifest') or opf_xml.find('opf:manifest')
                                if manifest:
                                    for el in manifest.find_all(['item', 'opf:item']):
                                        if el.get('id') == first_id:
                                            opf_dir = str(Path(opf_path).parent)
                                            pg = str(Path(opf_dir) / el.get('href')) if opf_dir else el.get('href')
                                            page_html = zf.read(pg).decode('utf-8', errors='replace')
                                            page_soup = BeautifulSoup(page_html, 'html.parser')
                                            imgs = page_soup.find_all('img')
                                            if imgs:
                                                pg_dir = str(Path(pg).parent)
                                                img_p = str(Path(pg_dir) / imgs[0].get('src')) if pg_dir else imgs[0].get('src')
                                                for item in book.get_items():
                                                    if item.get_type() == 1 and item.get_name():
                                                        if img_p.endswith(item.get_name().split('/')[-1]):
                                                            cover_id = item.get_id()
                                                            break
                                            break
                    zf.close()
                except Exception:
                    pass
            if cover_id:
                cover_item = book.get_item_with_id(cover_id)
                if cover_item:
                    cover_path = Path(filepath).parent / 'cover.jpg'
                    cover_path.write_bytes(cover_item.get_content())
                    metadata['cover_path'] = str(cover_path)
        except Exception:
            pass
    except Exception as e:
        import traceback
        print(f"EPUB metadata error: {e}")
        traceback.print_exc()
    return metadata


# ============ Main ============

if __name__ == '__main__':
    config.BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    config.COVERS_DIR.mkdir(parents=True, exist_ok=True)
    config.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    app.run(host='0.0.0.0', port=config.DEFAULT_PORT, debug=True)
