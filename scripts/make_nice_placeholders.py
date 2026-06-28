"""Create better-looking cover images for books without real covers."""
import sys, os, math
sys.path.insert(0, '/app')
from pathlib import Path
os.environ['VAULT_DIR'] = '/app/vault'
from app import get_session, Book, config
from PIL import Image, ImageDraw, ImageFont, ImageFilter

session = get_session()
books = session.query(Book).all()
generated = 0

def make_cover(title, author, year, slug):
    w, h = 600, 900
    
    # Generate a unique but stable color palette
    seed = sum(ord(c) for c in slug)
    hue1 = (seed * 37) % 360
    hue2 = (hue1 + 30 + (seed % 60)) % 360
    
    def hsl_to_rgb(h, s, l):
        h = h / 360
        s = s / 100
        l = l / 100
        if s == 0:
            return (int(l*255),)*3
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        return (
            int(hue2rgb(p, q, h + 1/3) * 255),
            int(hue2rgb(p, q, h) * 255),
            int(hue2rgb(p, q, h - 1/3) * 255),
        )
    
    c1 = hsl_to_rgb(hue1, 45, 35)
    c2 = hsl_to_rgb(hue2, 50, 25)
    
    img = Image.new('RGB', (w, h))
    for y in range(h):
        t = y / h
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(0, w, 3):
            img.putpixel((x, y), (r, g, b))
            img.putpixel((x+1, y), (r, g, b))
            img.putpixel((x+2, y), (r, g, b))
    
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    font_bold = None
    font_reg = None
    for path in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    ]:
        p = Path(path)
        if p.exists():
            try:
                if font_bold is None:
                    font_bold = ImageFont.truetype(str(p), 40)
                if font_reg is None:
                    font_reg = ImageFont.truetype(str(p), 24)
            except:
                pass
    
    if font_bold is None:
        font_bold = ImageFont.load_default()
        font_reg = ImageFont.load_default()
    
    # Subtle decorative border
    for bx in range(20, w-20):
        for by in [20, h-21]:
            if bx % 4 == 0:
                draw.point((bx, by), fill=(255,255,255,40))
    for by in range(20, h-20):
        for bx in [20, w-21]:
            if by % 4 == 0:
                draw.point((bx, by), fill=(255,255,255,40))
    
    # Decorative line
    line_y = 350
    for x in range(150, 451):
        alpha = 1.0 - abs(x - 300) / 150
        draw.point((x, line_y), fill=(255, 255, 255, int(60 * alpha)))
    
    # Title
    lines = []
    for word in title.split():
        if lines and font_bold.getlength(lines[-1] + ' ' + word) < 500:
            lines[-1] += ' ' + word
        else:
            lines.append(word)
    if not lines:
        lines = [title]
    
    y_start = 240 - (len(lines) - 1) * 25
    for i, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=font_bold)
        tw = bb[2] - bb[0]
        x = (w - tw) // 2
        draw.text((x, y_start + i * 55), line, fill='white', font=font_bold)
    
    # Author
    if author and author != 'Unknown':
        author_short = author.split(',')[0].split('&')[0].strip()[:25]
        bb = draw.textbbox((0, 0), author_short, font=font_reg)
        tw = bb[2] - bb[0]
        x = (w - tw) // 2
        draw.text((x, 420), author_short, fill=(255,255,255,160), font=font_reg)
    
    # Year
    if year:
        year_str = str(year)
        bb = draw.textbbox((0, 0), year_str, font=font_reg)
        tw = bb[2] - bb[0]
        x = (w - tw) // 2
        draw.text((x, 470), year_str, fill=(255,255,255,100), font=font_reg)
    
    # Bottom decorative text
    bottom = 'READING LIBRARY'
    try:
        small_font = ImageFont.truetype(str(list(Path('/usr/share/fonts/truetype/dejavu').glob('*.ttf'))[0]), 14)
    except:
        small_font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), bottom, font=small_font)
    tw = bb[2] - bb[0]
    x = (w - tw) // 2
    draw.text((x, h - 60), bottom, fill=(255,255,255,50), font=small_font)
    
    return img

for book in books:
    cover_path = config.COVERS_DIR / f"{book.slug}.jpg"
    
    # Only regenerate placeholders (small files)
    if cover_path.exists() and cover_path.stat().st_size >= 18000:
        continue
    
    img = make_cover(book.title, book.author, book.year, book.slug)
    img.save(cover_path, 'JPEG', quality=92)
    generated += 1
    print(f'  {book.title}')

session.close()
print(f'\nGenerated {generated} improved covers')
