#!/usr/bin/env python3
"""Нов шофьор от Viber текст + снимки → профил (10.11.2026).

Вход:  drivers/inbox/<slug>.txt   — отговорите на шофьора по drivers/TEMPLATE.txt
       drivers/inbox/<slug>/      — снимки (.jpg/.png/.webp) или base64 парчета
                                    <име>.b64.001, .002 … (MCP качва само текст)
Изход: drivers/profiles/<slug>.json — профилът (после build_drivers.py → сайта)
       img/<slug>_*.jpg              — смалени снимки, без EXIF (GPS, телефон)
       drivers/reports/<slug>.md     — какво е разчетено, какво е по подразбиране,
                                       какво казва регистърът на ИААА
След успех inbox файловете се трият (текстът остава в отчета).

Безопасност:
  - номер, който го няма в регистъра (или е с изтекло разрешително) → publish: false
  - slug, който започва с test- → винаги publish: false (за проби)
  - съществуващ профил със същия телефон → обновява се, id и основател се пазят
"""
import base64, datetime, glob, io, json, os, re, shutil, sys

INBOX, PROFILES, REPORTS = 'drivers/inbox', 'drivers/profiles', 'drivers/reports'
REGISTRY = 'data/registry.json'
FOUNDERS_UP_TO = 13          # първите 13 шофьора получават „Основател №N“
SOFIA = (42.6977, 23.3219)

# ── помощни ──────────────────────────────────────────────────────────────
LAT2CYR = str.maketrans('ABEKMHOPCTYX', 'АВЕКМНОРСТУХ')
CYR2LAT = str.maketrans('АВЕКМНОРСТУХ', 'ABEKMHOPCTYX')
TRANSLIT = dict(zip('абвгдежзийклмнопрстуфхцчшщъьюя',
    ['a','b','v','g','d','e','zh','z','i','y','k','l','m','n','o','p','r','s','t','u','f','h','ts','ch','sh','sht','a','y','yu','ya']))


def translit(s):
    out = ''
    for ch in s:
        lo = ch.lower()
        if lo in TRANSLIT:
            t = TRANSLIT[lo]
            out += t.capitalize() if ch != lo else t
        else:
            out += ch
    return out


def yes_no_ask(v):
    v = (v or '').strip().lower()
    if not v:
        return None
    if re.search(r'договар|питай|ask|може би|понякога|зависи|по договор', v):
        return 'ask'
    if re.match(r'(да|yes|y|ок|ok|разбира се|приемам)\b', v):
        return True
    if re.match(r'(не|no|n|без)\b', v):
        return False
    return 'ask'


def numbers(v):
    return [float(x.replace(',', '.')) for x in re.findall(r'\d+(?:[.,]\d+)?', v or '')]


def norm_phone(v):
    d = re.sub(r'\D', '', v or '')
    if d.startswith('00'):
        d = d[2:]
    if d.startswith('0'):
        d = '359' + d[1:]
    if len(d) == 9 and d[0] in '89':          # 888123456
        d = '359' + d
    return d


def norm_plate(v):
    p = re.sub(r'[\s\-]', '', (v or '').upper()).translate(CYR2LAT)
    m = re.fullmatch(r'([A-Z]{1,2})(\d{4})([A-Z]{1,2})', p)
    return (f'{m.group(1)} {m.group(2)} {m.group(3)}' if m else p), p.translate(LAT2CYR)


LANGS = [('бълг', 'bg'), ('англ', 'en'), ('немс', 'de'), ('френ', 'fr'), ('руск', 'ru'),
         ('чеш', 'cs'), ('итал', 'it'), ('испан', 'es'), ('турс', 'tr'), ('араб', 'ar'),
         ('китай', 'zh'), ('english', 'en'), ('german', 'de'), ('french', 'fr'),
         ('russian', 'ru'), ('italian', 'it'), ('spanish', 'es'), ('turkish', 'tr')]


# ── четене на Viber текста ───────────────────────────────────────────────
# началото на всеки етикет от TEMPLATE.txt — за да не се вземе етикетът за отговор
LABELS = {1: 'име', 2: 'телефон', 3: 'кола', 4: 'рег', 5: 'тип', 6: 'места',
          7: 'тарифа', 8: 'плащане', 9: 'езици', 10: 'летище', 11: 'домашни',
          12: 'пушиш', 13: 'две изречения'}
def parse_answers(text):
    """„7. Тарифа …: 1.49 / 0.75 / 0.85“ → {7: '1.49 / 0.75 / 0.85'}.
    Отговорът може да е на същия ред след „:“ или на следващите редове."""
    ans, cur = {}, None
    extra = {}
    for line in text.splitlines():
        m = re.match(r'\s*(\d{1,2})\s*[.)]\s*(.*)$', line)
        if m and 1 <= int(m.group(1)) <= 13:
            cur = int(m.group(1))
            rest = m.group(2).strip()
            if ':' in rest:
                ans[cur] = rest.split(':', 1)[1].strip()
            elif LABELS.get(cur) and rest.lower().startswith(LABELS[cur]):
                ans[cur] = ''                      # само етикетът, отговорът е отдолу
            else:
                ans[cur] = rest                    # „1. Иван Петров“ — без етикета
            continue
        m = re.match(r'\s*([A-Z_]{3,})\s*:\s*(.*)$', line)      # BIO_EN:, CITY: …
        if m:
            extra[m.group(1)] = m.group(2).strip()
            cur = None
            continue
        if cur and line.strip() and not line.strip().startswith(('📸', '🐟')):
            ans[cur] = (ans[cur] + ' ' + line.strip()).strip()
    return ans, extra


def build_profile(ans, extra, slug, old, notes):
    def note(msg):
        notes.append(msg)

    full = ans.get(1, '').strip()
    if not full:
        sys.exit(f'{slug}: липсва име (точка 1)')
    parts = full.split()
    is_cyr = bool(re.search(r'[А-Яа-я]', full))
    first, last = parts[0], (parts[-1] if len(parts) > 1 else '')
    name_bg = f'{first} {last[0]}.' if last else first
    lat_first, lat_last = translit(first), translit(last)
    name = f'{lat_first} {lat_last[0]}.' if last else lat_first
    if not is_cyr:
        name_bg = name
        note('Името е на латиница — name_bg е същото.')

    phone = norm_phone(ans.get(2))
    if not re.fullmatch(r'\d{10,13}', phone):
        sys.exit(f'{slug}: телефонът „{ans.get(2)}“ не изглежда като телефон')

    car = ans.get(3, '').strip() or '—'
    plate, plate_cyr = norm_plate(ans.get(4))

    t = (ans.get(5) or '').lower()
    t = re.sub(r'седан\s*[/,]\s*джип\s*(?:[/,]|или)\s*ван', ' ', t)   # етикетът от шаблона
    car_type = 'minivan' if re.search(r'ван|миниван|бус|van', t) else 'suv' if re.search(r'джип|suv|кросоувър', t) else 'sedan'
    if not t:
        note('Тип кола не е даден — седан.')
    seats = int((numbers(ans.get(6)) or [4])[0])
    if seats >= 6 and car_type == 'sedan':
        car_type = 'minivan'
        note(f'{seats} места → тип ван.')

    nums = numbers(ans.get(7))
    tariff, price = None, 'On request'
    if len(nums) >= 3:
        tariff = {'start': nums[0], 'km_day': nums[1], 'km_night': nums[2]}
    elif len(nums) == 2:
        tariff = {'start': nums[0], 'km_day': nums[1], 'km_night': nums[1]}
        note('Тарифата има 2 числа — нощната е приета равна на дневната.')
    else:
        note('Тарифата не е разчетена — „On request“.')
    if tariff:
        if not (0.3 <= tariff['km_day'] <= 3 and 0.3 <= tariff['km_night'] <= 3 and 0 < tariff['start'] <= 10):
            note(f'⚠ Тарифата изглежда странно: {tariff} — провери реда (старт / ден / нощ).')
        price = (f"{tariff['km_day']:.2f} EUR/km day / {tariff['km_night']:.2f} EUR/km night / "
                 f"Start {tariff['start']:.2f} EUR")

    p = (ans.get(8) or '').lower()
    payment = []
    if re.search(r'кеш|брой|cash|в брой', p): payment.append('cash')
    if re.search(r'карт|терминал|pos|card|пос', p): payment.append('terminal')
    if re.search(r'revolut|револют', p): payment.append('revolut')
    if not payment:
        payment = ['cash']
        note('Плащане не е разчетено — само кеш.')

    l = (ans.get(9) or '').lower()
    langs = ['bg'] + [code for key, code in LANGS if key in l and code != 'bg']
    langs = list(dict.fromkeys(langs))

    trip = re.split(r'[/,;]', ans.get(10) or '')
    trip = [yes_no_ask(x) for x in trip if x.strip()]
    if len(trip) == 1:
        trip = trip * 3
    airport, longdist, night = (trip + ['ask', 'ask', 'ask'])[:3]

    pets = yes_no_ask(ans.get(11))
    smokes = yes_no_ask(ans.get(12)) is True

    bio_bg = ' '.join((ans.get(13) or '').split())
    bio_en = extra.get('BIO_EN', '').strip()
    if bio_bg and not bio_en:
        bio_en = bio_bg
        note('Няма BIO_EN — английското описание е същото като българското. Добави превод.')

    base = dict(old) if old else {}
    prof = {
        'slug': slug, 'publish': True,
        'id': base.get('id'), 'gps_id': phone,
        'name': name, 'name_bg': name_bg,
        'avatar': base.get('avatar', ''), 'photos': base.get('photos', []),
        'city': extra.get('CITY', base.get('city', 'sofia')).lower(),
        'lat': base.get('lat', SOFIA[0]), 'lng': base.get('lng', SOFIA[1]),
        'car': car, 'plate': plate, 'car_type': car_type,
        # 0 би дало значка „Спорт“ (accel<5); 10 → „Комфорт“, без цифри на екрана
        'accel': float(extra['ACCEL']) if extra.get('ACCEL') else base.get('accel', 10.0), 'seats': seats,
        'online': False, 'rating': base.get('rating', 5.0), 'reviews': base.get('reviews', 0),
        'payment': payment, 'langs': langs,
        'electric': bool(re.search(r'tesla|тесла|id\.?\s?[3-7]|leaf|лийф|ioniq|e-?niro|kona|zoe|enyaq|model [3sxy]|byd|polestar|ev\b|електр', car.lower())),
        'smoking': smokes, 'nosmoker': not smokes,
        'petfriendly': pets if pets is not None else 'ask',
        'childok': base.get('childok', False),
        'sport': False, 'fast': False, 'comfort': True,
        'minivan': car_type == 'minivan', 'suv': car_type == 'suv', 'luxury': False,
        'ac': True, 'music': True, 'chalga': False, 'nomusic': False,
        'silent_ok': True, 'talk_ok': True, 'calm_ok': True,
        'terminal': 'terminal' in payment,
        'music_pop': True, 'music_chalga': False, 'music_rock': True, 'music_classical': False,
        'music_jazz': False, 'music_electronic': False, 'music_chillout': True, 'music_lounge': False,
        'airport': airport, 'longdist': longdist, 'night': night,
        'business': False, 'legroom': False, 'panoroof': False, 'streaming': False,
        'usb': True, 'tinted': False, 'wheelchair': 'ask', 'verified': False,
        'areas': base.get('areas', 'Sofia — Center, Airport, Ring Road, All districts'),
        'phone': '+' + phone, 'price': price,
        'bio': bio_en, 'bio_bg': bio_bg,
    }
    if tariff:
        prof['tariff'] = tariff
    # ръчни подобрения в стария профил (музика, климатик…) не се губят при обновяване
    for k, v in base.items():
        if k not in prof or k in ('founder', 'tariff_photo', 'bio_key', 'accel'):
            prof[k] = v
    return prof, plate_cyr


def check_registry(plate_cyr, notes):
    try:
        reg = json.load(io.open(REGISTRY, encoding='utf-8'))
    except Exception as e:
        notes.append(f'⚠ Регистърът не се чете: {e}')
        return None
    for r in reg['v']:
        if r[0].replace(' ', '') == plate_cyr:
            return {'model': reg['mods'][r[1]], 'operator': reg['ops'][r[2]], 'year': r[3],
                    'valid_to': r[4], 'source': reg.get('source'), 'generated': reg.get('generated')}
    return None


# ── снимки ───────────────────────────────────────────────────────────────
def assemble_b64(folder):
    """photo.jpg.b64.001 + .002 … → photo.jpg"""
    groups = {}
    for f in glob.glob(os.path.join(folder, '*.b64.*')):
        m = re.match(r'(.+)\.b64\.(\d+)$', f)
        if m:
            groups.setdefault(m.group(1), []).append((int(m.group(2)), f))
    for target, chunks in groups.items():
        data = ''.join(io.open(f, encoding='ascii').read().strip() for _, f in sorted(chunks))
        open(target, 'wb').write(base64.b64decode(data))
        for _, f in chunks:
            os.remove(f)


def role(name):
    n = name.lower()
    if re.search(r'avatar|face|lice|лице|portrait|аз\b', n): return 'avatar'
    if re.search(r'tarif|тариф|price|цени', n): return 'tariff'
    return 'photo'


def process_photos(slug, folder, notes, old=None):
    from PIL import Image, ImageOps
    if not os.path.isdir(folder):
        return None
    assemble_b64(folder)
    files = sorted(f for f in glob.glob(os.path.join(folder, '*'))
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic')))
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

    def save(src, dst, square=None, longest=1280):
        im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')   # завърта; EXIF не се пази
        if square:
            im = ImageOps.fit(im, (square, square), Image.LANCZOS)
        else:
            im.thumbnail((longest, longest), Image.LANCZOS)
        im.save(dst, 'JPEG', quality=80, optimize=True, progressive=True)
        return dst, os.path.getsize(dst)

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


# точка от шаблона → полета в профила (за частично обновяване)
FIELDS = {1: ('name', 'name_bg'), 3: ('car', 'electric'), 4: ('plate',),
          5: ('car_type', 'minivan', 'suv'), 6: ('seats',), 7: ('tariff', 'price'),
          8: ('payment', 'terminal'), 9: ('langs',), 10: ('airport', 'longdist', 'night'),
          11: ('petfriendly',), 12: ('smoking', 'nosmoker'), 13: ('bio', 'bio_bg')}
DEFAULT_NOTES = ('Тип кола не е даден', 'Плащане не е разчетено', 'Тарифата не е разчетена',
                 'Няма BIO_EN', 'Името е на латиница')

# ── главно ───────────────────────────────────────────────────────────────
def existing_profiles():
    out = {}
    for f in glob.glob(os.path.join(PROFILES, '*.json')):
        p = json.load(io.open(f, encoding='utf-8'))
        out[p.get('gps_id')] = (f, p)
    return out


def intake(txt_path):
    slug = re.sub(r'[^a-z0-9-]', '', os.path.basename(txt_path)[:-4].lower())
    inbox_slug = slug          # папката със снимките е по името на файла, дори при обновяване
    notes = []
    text = io.open(txt_path, encoding='utf-8').read()
    ans, extra = parse_answers(text)

    profiles = existing_profiles()
    phone = norm_phone(ans.get(2))
    old_path, old = profiles.get(phone, (None, None))
    if old and old.get('slug') and old['slug'] != slug:
        notes.append(f'Телефонът вече е на „{old["slug"]}“ — обновявам него.')
        slug = old['slug']

    prof, plate_cyr = build_profile(ans, extra, slug, old, notes)
    if old:
        # обновяване: пипат се само полетата, които ги има в съобщението
        kept = []
        for n, keys in FIELDS.items():
            if not (ans.get(n) or '').strip():
                for k in keys:
                    if k in old:
                        prof[k] = old[k]
                    else:
                        prof.pop(k, None)
                kept.append(str(n))
        if 'BIO_EN' not in extra and 'bio' in old and (ans.get(13) or '').strip() == old.get('bio_bg'):
            prof['bio'] = old['bio']
        notes[:] = [n for n in notes if not n.startswith(DEFAULT_NOTES)]
        if kept:
            notes.append('Обновяване — непроменени точки: ' + ', '.join(kept))
        plate_cyr = norm_plate(prof['plate'])[1]

    if prof['id'] is None:
        ids = [p.get('id', 0) for _, p in profiles.values()]
        prof['id'] = max(ids + [0]) + 1

    reg = check_registry(plate_cyr, notes)
    today = datetime.date.today().isoformat()
    if reg and (reg['valid_to'] or '') >= today:
        prof['verified'] = True
    else:
        prof['publish'] = False
        prof['verified'] = False
        if reg:
            notes.append(f'⚠ Разрешителното е валидно до {reg["valid_to"]} — изтекло. Профилът НЕ е публикуван.')
        else:
            notes.append(f'⚠ Номер {prof["plate"]} го няма в регистъра на ИААА (София). Профилът НЕ е публикуван. '
                         'Ако е вярно (друг град, нова кола) — сложи "publish": true в профила.')
    if slug.startswith('test-'):
        prof['publish'] = False
        notes.append('Тестов профил (test-) — не се публикува.')
    # „Основател №N“ — поредният номер сред публикуваните, до FOUNDERS_UP_TO
    if prof['publish'] and 'founder' not in prof:
        taken = [p.get('founder', 0) for _, p in profiles.values()]
        nxt = max(taken + [0]) + 1
        if nxt <= FOUNDERS_UP_TO:
            prof['founder'] = nxt

    ph = process_photos(slug, os.path.join(INBOX, inbox_slug), notes, old)
    if ph:
        prof.update(ph)
    if not prof.get('avatar'):
        prof['avatar'] = 'img/icon-192.png'
        notes.append('⚠ Няма снимки — временно иконката на fish.taxi.')

    os.makedirs(PROFILES, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    io.open(os.path.join(PROFILES, f'{slug}.json'), 'w', encoding='utf-8').write(
        json.dumps(prof, ensure_ascii=False, indent=1) + '\n')

    rep = [f'# {prof["name_bg"]} ({prof["name"]}) — {today}', '',
           f'**{"✅ Публикуван" if prof["publish"] else "⏸ НЕ е публикуван"}** · id {prof["id"]}'
           + (f' · Основател №{prof["founder"]}' if prof.get('founder') else ''), '',
           '| Поле | Стойност |', '|---|---|']
    def human(v):
        if v is True: return 'да'
        if v is False: return 'не'
        if v == 'ask': return 'по договаряне'
        if isinstance(v, list): return ', '.join(map(str, v))
        return v
    for k, label in (('phone', 'Телефон'), ('car', 'Кола'), ('plate', 'Номер'), ('car_type', 'Тип'),
                     ('seats', 'Места'), ('price', 'Тарифа'), ('payment', 'Плащане'), ('langs', 'Езици'),
                     ('airport', 'Летище'), ('longdist', 'Дълги курсове'), ('night', 'Нощем'),
                     ('petfriendly', 'Любимци'), ('nosmoker', 'Непушач'), ('electric', 'Електрическа')):
        rep.append(f'| {label} | {human(prof.get(k))} |')
    rep += ['', '## Регистър на ИААА', '']
    rep.append(f'{reg["model"]} · {reg["operator"]} · {reg["year"]} · валидно до {reg["valid_to"]} '
               f'(източник {reg["source"]})' if reg else 'Не е намерен.')
    if reg and reg['model'] and prof['car'] != '—':
        words = [w for w in re.findall(r'\w{3,}', prof['car'].upper().translate(LAT2CYR))]
        if words and not any(w in reg['model'] for w in words):
            rep.append(f'\n⚠ Колата в отговора („{prof["car"]}“) не съвпада с регистъра — провери.')
    rep += ['', '## Бележки', ''] + [f'- {n}' for n in notes]
    rep += ['', '## Остава', '',
            f'- [ ] Токен за GPS: админ → Добави шофьор, телефон {prof["phone"]}',
            '- [ ] Шофьорът инсталира приложението и влиза с ID + токен']
    if 'BIO_EN' not in extra:
        rep.append('- [ ] Превод на описанието (поле "bio" в профила)')
    rep += ['', '---', '', 'Оригиналният текст:', '', '```', text.strip(), '```']
    io.open(os.path.join(REPORTS, f'{slug}.md'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')

    os.remove(txt_path)
    shutil.rmtree(os.path.join(INBOX, inbox_slug), ignore_errors=True)
    print(f'{slug}: {"публикуван" if prof["publish"] else "НЕ е публикуван"} · id {prof["id"]} · '
          f'отчет drivers/reports/{slug}.md')
    for n in notes:
        print('   ', n)


def main():
    todo = sorted(glob.glob(os.path.join(INBOX, '*.txt')))
    if not todo:
        print('inbox е празен')
    for t in todo:
        intake(t)


if __name__ == '__main__':
    main()
