#!/usr/bin/env python3
"""FT-ICONS-V1 (10.11.2026) — иконките в истинския им размер.

favicon.png, img/icon-192.png и img/icon-512.png бяха едно и също
изображение 1254×1254, по 848 KB всяко. index.html ползва icon-192 дори
като 14-пикселова иконка в бутоните, а manifest.json обявява 192×192 и
512×512. Първото отваряне на fish.taxi теглеше ~1.7 MB само за иконки.

Смаляваме до 64 / 192 / 512 px и вдигаме ?v= на favicon-а, за да го
изтеглят наново браузърите. Идемпотентен: пипа само файлове с грешен размер.
"""
import io, subprocess, sys

import shutil, struct

def png_size(path):
    # ширина и височина от IHDR — без библиотеки
    with open(path, 'rb') as f:
        head = f.read(24)
    return struct.unpack('>II', head[16:24])

def get_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        pass
    # системният Python на runner-а може да отказва pip (PEP 668)
    for extra in (['--break-system-packages'], ['--user', '--break-system-packages'], []):
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', *extra, 'pillow'])
        if r.returncode == 0:
            try:
                from PIL import Image
                return Image
            except ImportError:
                pass
    return None

Image = get_pil()
magick = shutil.which('magick') or shutil.which('convert')
print('инструмент:', 'Pillow' if Image else (magick or 'НЯМА'))
if not Image and not magick:
    sys.exit('нито Pillow, нито ImageMagick')

TARGETS = [('favicon.png', 64), ('img/icon-192.png', 192), ('img/icon-512.png', 512)]
changed = 0
for path, size in TARGETS:
    before = png_size(path)
    if before == (size, size):
        print(path, ': вече е', size, 'px')
        continue
    if Image:
        im = Image.open(path)
        im = im.convert('RGBA') if im.mode in ('P', 'LA') else im
        im.resize((size, size), Image.LANCZOS).save(path, optimize=True)
    else:
        subprocess.run([magick, path, '-resize', f'{size}x{size}!', '-strip', path], check=True)
    after = png_size(path)
    if after != (size, size):
        sys.exit(f'{path}: очаквах {size}, стана {after}')
    changed += 1
    print(path, ':', before, '→', after)

for page in ('index.html', 'next/index.html'):
    try:
        s = io.open(page, encoding='utf-8').read()
    except FileNotFoundError:
        continue
    if 'favicon.png?v=2' in s:
        io.open(page, 'w', encoding='utf-8').write(s.replace('favicon.png?v=2', 'favicon.png?v=3'))
        print(page, ': favicon ?v=3')

print('иконки сменени:', changed)