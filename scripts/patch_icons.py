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

try:
    from PIL import Image
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 'pillow'], check=True)
    from PIL import Image

TARGETS = [('favicon.png', 64), ('img/icon-192.png', 192), ('img/icon-512.png', 512)]
changed = 0
for path, size in TARGETS:
    im = Image.open(path)
    before = im.size
    if before == (size, size):
        print(path, ': вече е', size, 'px')
        continue
    im = im.convert('RGBA') if im.mode in ('P', 'LA') else im
    im = im.resize((size, size), Image.LANCZOS)
    im.save(path, optimize=True)
    changed += 1
    print(path, ':', before, '→', (size, size))

for page in ('index.html', 'next/index.html'):
    try:
        s = io.open(page, encoding='utf-8').read()
    except FileNotFoundError:
        continue
    if 'favicon.png?v=2' in s:
        io.open(page, 'w', encoding='utf-8').write(s.replace('favicon.png?v=2', 'favicon.png?v=3'))
        print(page, ': favicon ?v=3')

print('иконки сменени:', changed)
