#!/usr/bin/env python3
"""Снимките на шофьора: сглобяване, проверка, смаляване (10.11.2026).

Ползва се от driver_intake.py (inbox → сайта) и prep_photos.py (чат → inbox).

Снимките стигат до репото по един от два начина:
  - направо като .jpg/.webp (git push — байтовете не минават през модела);
  - като base64 парчета <име>.b64.001, .002 … (GitHub MCP качва само текст).
При парчетата photos.sha256 (формат на sha256sum) пази отпечатъка на всяка
снимка. Ако сглобената снимка не съвпада или парче липсва — шофьорът чака,
нищо не се трие, отчетът казва кое да се качи пак.
"""
import base64, binascii, glob, hashlib, io, os, re

MANIFEST = 'photos.sha256'
IMG_EXT = ('.jpg', '.jpeg', '.png', '.webp', '.heic')


def blob_sha(data):
    """SHA на файла в git — същото като content_sha, което връща put_file."""
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def read_manifest(folder):
    out = {}
    p = os.path.join(folder, MANIFEST)
    if os.path.exists(p):
        for line in io.open(p, encoding='ascii', errors='replace'):
            m = re.match(r'\s*([0-9a-fA-F]{64})\s+\*?(\S+)', line)
            if m:
                out[m.group(2)] = m.group(1).lower()
    return out


def assemble(folder):
    """Сглобява парчетата. Връща списък с проблеми; празен = всичко е наред.
    Трие парчетата само ако снимката е сглобена и проверена."""
    if not os.path.isdir(folder):
        return []
    manifest = read_manifest(folder)
    groups, problems = {}, []
    for f in glob.glob(os.path.join(folder, '*.b64.*')):
        m = re.match(r'(.+)\.b64\.(\d+)$', f)
        if m:
            groups.setdefault(m.group(1), []).append((int(m.group(2)), f))
    for target, chunks in sorted(groups.items()):
        name = os.path.basename(target)
        nums = sorted(n for n, _ in chunks)
        have = ', '.join(f'{n:03d}' for n in nums)
        if nums != list(range(1, len(nums) + 1)):
            problems.append(f'{name}: липсва парче (има {have})')
            continue
        text = ''.join(io.open(f, encoding='ascii', errors='replace').read().strip()
                       for _, f in sorted(chunks))
        try:
            data = base64.b64decode(text, validate=True)
        except (binascii.Error, ValueError) as e:
            problems.append(f'{name}: base64 е повреден ({e}) — парчета {have}; '
                            'сравни content_sha на всяко с очакваното и качи пак разминалото се')
            continue
        want = manifest.get(name)
        if want and hashlib.sha256(data).hexdigest() != want:
            problems.append(f'{name}: отпечатъкът не съвпада с {MANIFEST} — парчета {have}; '
                            'сравни content_sha на всяко с очакваното')
            continue
        open(target, 'wb').write(data)
        for _, f in chunks:
            os.remove(f)
    for name in manifest:
        if not os.path.exists(os.path.join(folder, name)) and name not in {
                os.path.basename(t) for t in groups}:
            problems.append(f'{name}: няма нито снимка, нито парчета')
    if problems:
        return problems
    for f in glob.glob(os.path.join(folder, '*')):
        if f.lower().endswith(IMG_EXT):
            try:
                from PIL import Image
                Image.open(f).verify()
            except Exception as e:
                problems.append(f'{os.path.basename(f)}: не се отваря като снимка ({e})')
    return problems


def role(name):
    n = name.lower()
    if re.search(r'avatar|face|lice|лице|portrait|аз\b', n): return 'avatar'
    if re.search(r'tarif|тариф|price|цени', n): return 'tariff'
    return 'photo'


def save(src, dst, square=None, longest=1280):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')   # завърта; EXIF не се пази
    if square:
        im = ImageOps.fit(im, (square, square), Image.LANCZOS)
    else:
        im.thumbnail((longest, longest), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
    return dst, os.path.getsize(dst)


def process_photos(slug, folder, notes, old=None):
    """Вече сглобените снимки → img/<slug>_*.jpg. None, ако няма снимки."""
    if not os.path.isdir(folder):
        return None
    files = sorted(f for f in glob.glob(os.path.join(folder, '*')) if f.lower().endswith(IMG_EXT))
    if not files:
        return None
    avatar = next((f for f in files if role(os.path.basename(f)) == 'avatar'), None)
    if avatar is None and not old:
        avatar = files[0]          # нов шофьор: първата снимка е лицето
    tariff = next((f for f in files if role(os.path.basename(f)) == 'tariff' and f != avatar), None)
    photos = [f for f in files if f not in (avatar, tariff)]
    # обновяване: новите снимки се добавят към старите (до 6); лице и тарифа —
    # само ако името на файла го казва
    out = {'photos': list((old or {}).get('photos', []))[:6]}
    start = len(out['photos'])
    if avatar:
        dst, sz = save(avatar, f'img/{slug}_avatar.jpg', square=400)
        out['avatar'] = dst
        notes.append(f'Лице: {os.path.basename(avatar)} → {dst} ({sz // 1024} KB)')
    for i, f in enumerate(photos, start + 1):
        if len(out['photos']) >= 6:
            notes.append(f'Снимка {os.path.basename(f)} е пропусната — максимум 6')
            continue
        dst, sz = save(f, f'img/{slug}_{i}.jpg')
        if dst not in out['photos']:
            out['photos'].append(dst)
        notes.append(f'Снимка {i}: {os.path.basename(f)} → {dst} ({sz // 1024} KB)')
    if tariff:
        dst, sz = save(tariff, f'img/{slug}_tariff.jpg')
        out['tariff_photo'] = dst
        notes.append(f'Тарифа: {os.path.basename(tariff)} → {dst} ({sz // 1024} KB)')
    return out
