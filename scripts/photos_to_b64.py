#!/usr/bin/env python3
"""Снимки от чата → base64 парчета за drivers/inbox/<slug>/ (10.11.2026).

GitHub MCP качва само текст и до ~25 KB на файл. Затова снимката се смалява
тук, EXIF се маха (GPS на дома на шофьора!), и се реже на парчета по 20 000
знака. driver_intake.py ги сглобява обратно.

  python3 scripts/photos_to_b64.py <slug> лице.jpg кола.jpg салон.jpg тарифа.jpg

Редът на снимките има значение: 1 = лице, 2…n-1 = кола/салон, последната с
„тариф“ в името = табелата. Имената стават 1-lice.jpg, 2-kola.jpg … ,
N-tarifa.jpg. Изходът е в /tmp/b64/<slug>/ — всеки файл се качва с put_file
на пътя drivers/inbox/<slug>/<име на файла>.
"""
import base64, os, sys
from PIL import Image, ImageOps

CHUNK = 20000


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    slug, files = sys.argv[1], sys.argv[2:]
    out = f'/tmp/b64/{slug}'
    os.makedirs(out, exist_ok=True)
    names = []
    for i, src in enumerate(files, 1):
        low = os.path.basename(src).lower()
        if i == 1:
            name = '1-lice.jpg'
        elif 'тариф' in low or 'tarif' in low or (i == len(files) and len(files) >= 4):
            name = f'{i}-tarifa.jpg'
        else:
            name = f'{i}-snimka.jpg'
        im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
        im.thumbnail((1600, 1600), Image.LANCZOS)
        tmp = os.path.join(out, name)
        im.save(tmp, 'JPEG', quality=82, optimize=True)      # без exif=
        b = base64.b64encode(open(tmp, 'rb').read()).decode()
        os.remove(tmp)
        parts = [b[j:j + CHUNK] for j in range(0, len(b), CHUNK)]
        for n, part in enumerate(parts, 1):
            p = os.path.join(out, f'{name}.b64.{n:03d}')
            open(p, 'w').write(part)
            names.append(p)
        print(f'{src} → {name}: {len(parts)} парчета')
    print(f'\n{len(names)} файла за качване в drivers/inbox/{slug}/ (снимките ПРЕДИ текста):')
    for p in names:
        print('  ', p)


if __name__ == '__main__':
    main()
