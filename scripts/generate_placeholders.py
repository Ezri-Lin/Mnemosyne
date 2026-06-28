"""Generate placeholder covers for books without them."""
import sys, os
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config
from PIL import Image, ImageDraw, ImageFont

session = get_session()
books = session.query(Book).all()

config.COVERS_DIR.mkdir(parents=True, exist_ok=True)
generated = 0

palettes = [
    ('#b9422f', '#c2872d'), ('#245f73', '#4d6f48'),
    ('#4d6f48', '#c2872d'), ('#c2872d', '#b9422f'),
    ('#b9422f', '#171411'), ('#245f73', '#171411'),
    ('#6d6258', '#c2872d'), ('#4d6f48', '#245f73'),
]

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    if cover_path.exists():
        continue
    
    idx = abs(hash(book.slug)) % len(palettes)
    c1, c2 = palettes[idx]
    
    img = Image.new('RGB', (600, 900))
    for y in range(900):
        r = int(int(c1[1:3], 16) * (1 - y/900) + int(c2[1:3], 16) * (y/900))
        g = int(int(c1[3:5], 16) * (1 - y/900) + int(c2[3:5], 16) * (y/900))
        b = int(int(c1[5:7], 16) * (1 - y/900) + int(c2[5:7], 16) * (y/900))
        for x in range(600):
            img.putpixel((x, y), (r, g, b))
    
    draw = ImageDraw.Draw(img)
    
    # Title text
    title = book.title
    font_size = 36 if len(title) > 12 else 48
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
    except:
        font = ImageFont.load_default()
    
    # Split title into lines
    words = title.split()
    lines = []
    line = ''
    for w in words:
        test = line + ' ' + w if line else w
        bb = draw.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] > 500:
            lines.append(line)
            line = w
        else:
            line = test
    lines.append(line)
    
    y = 300
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (600 - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, fill='white', font=font)
        y += font_size + 8
    
    # Author
    if book.author and book.author != 'Unknown':
        try:
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except:
            font_small = ImageFont.load_default()
        author_text = book.author.split(',')[0].split('&')[0].strip()[:30]
        bb = draw.textbbox((0, 0), author_text, font=font_small)
        x = (600 - (bb[2] - bb[0])) // 2
        draw.text((x, y + 20), author_text, fill=(255,255,255,180), font=font_small)
    
    # Year
    if book.year:
        year_text = str(book.year)
        bb = draw.textbbox((0, 0), year_text, font=font_small)
        x = (600 - (bb[2] - bb[0])) // 2
        draw.text((x, y + 55), year_text, fill=(255,255,255,120), font=font_small)
    
    img.save(cover_path, 'JPEG', quality=85)
    generated += 1

session.close()
print(f'Generated {generated} placeholder covers')
