#!/usr/bin/env python3
"""Снимки от чата → готови за drivers/inbox/<slug>/ (10.11.2026).

  python3 scripts/prep_photos.py <slug> лице.jpg кола.jpg салон.jpg тарифа.jpg
  python3 scripts/prep_photos.py --direct <репо> <slug> лице.jpg …
  python3 scripts/prep_photos.py --add <slug> кола2.jpg   (още снимки към стар профил)

Редът има значение: 1-ва = лицето, последната (ако са 4+) или с „тариф“ в
името = табелата с тарифата, другите = кола/салон. С --add лицето и тарифата
се сменят само ако името на файла го казва (лице/lice, тариф/tarif).

Всяка снимка се завърта правилно, смалява (лице 400×400, другите до 960 px),
записва като WebP и **губи EXIF** — в него често е GPS-ът на дома на шофьора,
а репото е публично. Сурови снимки не се качват никога.

--direct  пише снимките направо в <репо>/drivers/inbox/<slug>/ — за git push
          (когато сесията има достъп за писане до репото). Най-евтино.
иначе     base64 парчета по 20 000 знака + photos.sha256 в /tmp/b64/<slug>/ —
          за качване с GitHub MCP put_file. Скриптът печата очаквания
          content_sha на всеки файл: ако put_file върне друг, файлът е
          преписан грешно → качи го пак, преди да качиш текста.
"""
import base64, hashlib, io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver_photos import MANIFEST, blob_sha
from PIL import Image, ImageOps

CHUNK = 20000


def prepare(src, name):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    if '-lice' in name:
        im = ImageOps.fit(im, (400, 400), Image.LANCZOS)
        q = 78
    else:
        im.thumbnail((960, 960), Image.LANCZOS)
        q = 75 if 'tarifa' in name else 68          # тарифата трябва да се чете
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6)       # без exif=
    return buf.getvalue()


def main():
    args = sys.argv[1:]
    direct, add = None, False
    while args[:1] in (['--direct'], ['--add']):
        if args[0] == '--add':
            add, args = True, args[1:]
        else:
            direct, args = args[1], args[2:]
    if len(args) < 2:
        sys.exit(__doc__)
    slug, files = args[0], args[1:]
    out = os.path.join(direct, 'drivers', 'inbox', slug) if direct else f'/tmp/b64/{slug}'
    if not direct and os.path.isdir(out):                # стари парчета от предишно пускане
        for f in os.listdir(out):
            os.remove(os.path.join(out, f))
    os.makedirs(out, exist_ok=True)
    manifest, upload = [], []
    for i, src in enumerate(files, 1):
        low = os.path.basename(src).lower()
        if (i == 1 and not add) or 'лице' in low or 'lice' in low:
            name = f'{i}-lice.webp'
        elif 'тариф' in low or 'tarif' in low or (i == len(files) and len(files) >= 4 and not add):
            name = f'{i}-tarifa.webp'
        else:
            name = f'{i}-snimka.webp'
        data = prepare(src, name)
        if direct:
            open(os.path.join(out, name), 'wb').write(data)
            print(f'{src} → {out}/{name} ({len(data) // 1024} KB)')
            continue
        manifest.append(f'{hashlib.sha256(data).hexdigest()}  {name}\n')
        b = base64.b64encode(data).decode()
        for n, j in enumerate(range(0, len(b), CHUNK), 1):
            fn = f'{name}.b64.{n:03d}'
            open(os.path.join(out, fn), 'w').write(b[j:j + CHUNK])
            upload.append((fn, b[j:j + CHUNK].encode()))
        print(f'{src} → {name}: {len(data) // 1024} KB, {len(b)} знака base64')
    if direct:
        return
    m = ''.join(manifest)
    open(os.path.join(out, MANIFEST), 'w').write(m)
    upload.append((MANIFEST, m.encode()))
    total = sum(len(d) for _, d in upload)
    print(f'\n{len(upload)} файла, {total // 1000} хил. знака. Качи ги в drivers/inbox/{slug}/ '
          f'в този ред, ПРЕДИ текста. Очакван content_sha:')
    for fn, d in upload:
        print(f'  {blob_sha(d)}  {out}/{fn}')


if __name__ == '__main__':
    main()
