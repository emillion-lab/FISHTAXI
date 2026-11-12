#!/usr/bin/env python3
"""Сглобява DRIVERS в index.html от drivers/profiles/*.json (10.11.2026).

Източникът на истина за шофьорите са отделните файлове в drivers/profiles/.
Този скрипт ги чете, проверява и записва масива `var DRIVERS=[...]` в
index.html. Ръчна редакция на DRIVERS в index.html се губи при следващо
пускане — пипа се профилът, не страницата.

  publish: false  → профилът се пази, но не излиза на сайта
  slug, publish, ключове с _ → само вътрешни, не стигат до страницата

Идемпотентен. Спира с грешка (и не пише нищо), ако профил е счупен.
"""
import glob, io, json, os, sys

PROFILES = 'drivers/profiles'
PAGE = 'index.html'
INTERNAL = {'slug', 'publish'}

REQUIRED = {
    'id': int, 'gps_id': str, 'name': str, 'name_bg': str, 'avatar': str,
    'photos': list, 'city': str, 'lat': (int, float), 'lng': (int, float),
    'car': str, 'plate': str, 'car_type': str, 'seats': int,
    'payment': list, 'langs': list, 'phone': str, 'price': str, 'areas': str,
}
CAR_TYPES = {'sedan', 'suv', 'minivan'}
PAYMENTS = {'cash', 'terminal', 'revolut'}


def load_profiles():
    out, errors = [], []
    for path in sorted(glob.glob(os.path.join(PROFILES, '*.json'))):
        if os.path.basename(path).startswith('_'):
            continue
        try:
            p = json.load(io.open(path, encoding='utf-8'))
        except Exception as e:
            errors.append(f'{path}: невалиден JSON — {e}')
            continue
        for k, t in REQUIRED.items():
            if k not in p:
                errors.append(f'{path}: липсва „{k}“')
            elif not isinstance(p[k], t) or isinstance(p[k], bool) and t is int:
                errors.append(f'{path}: „{k}“ е {type(p[k]).__name__}')
        if p.get('car_type') not in CAR_TYPES:
            errors.append(f'{path}: car_type трябва да е {sorted(CAR_TYPES)}')
        bad_pay = set(p.get('payment') or []) - PAYMENTS
        if bad_pay:
            errors.append(f'{path}: непознато плащане {sorted(bad_pay)}')
        for img in [p.get('avatar')] + list(p.get('photos') or []) + [p.get('tariff_photo')]:
            if img and not img.startswith('http') and not os.path.exists(img):
                errors.append(f'{path}: няма такава снимка {img}')
        out.append((path, p))
    ids = [p['id'] for _, p in out if isinstance(p.get('id'), int)]
    for i in set(ids):
        if ids.count(i) > 1:
            errors.append(f'id {i} се повтаря')
    gps = [p.get('gps_id') for _, p in out]
    for g in set(gps):
        if g and gps.count(g) > 1:
            errors.append(f'gps_id {g} се повтаря')
    return out, errors


def public(p):
    d = {k: v for k, v in p.items() if k not in INTERNAL and not k.startswith('_')}
    if 'smoking' in d:
        d['smoking'] = False   # пушене в такси е забранено — никога „пушене OK“
    return d


def render(drivers):
    # един шофьор на ред-блок — четимо в diff-а, валиден JSON
    parts = [json.dumps(d, ensure_ascii=False) for d in drivers]
    return '[\n' + ',\n'.join(parts) + '\n]'


def replace_array(s, new_arr):
    key = 'var DRIVERS='
    i = s.find(key)
    if i < 0 or s.count(key) != 1:
        sys.exit('index.html: „var DRIVERS=“ не е намерено точно веднъж')
    start = i + len(key)
    _, end = json.JSONDecoder().raw_decode(s, start)
    return s[:start] + new_arr + s[end:]


# Описанието на български: bio_bg за bg, иначе bio (EN). Еднократна поправка.
BIO_OLD = "(d.bio_key&&t[d.bio_key])?t[d.bio_key]:(d.bio||'')"
BIO_NEW = "(d.bio_key&&t[d.bio_key])?t[d.bio_key]:((lang==='bg'&&d.bio_bg)||d.bio||'')"


def main():
    profiles, errors = load_profiles()
    if errors:
        print('ПРОФИЛИТЕ ИМАТ ГРЕШКИ — index.html не е пипан:')
        print('\n'.join('  - ' + e for e in errors))
        sys.exit(1)
    live = [public(p) for _, p in profiles if p.get('publish', True) is not False]
    hidden = [p.get('slug') or path for path, p in profiles if p.get('publish', True) is False]
    live.sort(key=lambda d: d['id'])

    # От v3 (12.11.2026) началната страница чете data/drivers.json и няма вграден
    # масив. Старият сайт живее в classic.html — вграждаме там, където го има.
    page = next((f for f in (PAGE, 'classic.html')
                 if os.path.exists(f) and io.open(f, encoding='utf-8').read().count('var DRIVERS=') == 1), None)
    if page is None:
        print(f'няма страница с вграден DRIVERS — само data/drivers.json ({len(live)} на сайта)')
    else:
        s = io.open(page, encoding='utf-8').read()
        new = replace_array(s, render(live))
        if BIO_OLD in new:
            new = new.replace(BIO_OLD, BIO_NEW)
        if new != s:
            io.open(page, 'w', encoding='utf-8').write(new)
            print(f'{page}: DRIVERS обновен — {len(live)} на сайта')
        else:
            print(f'{page}: без промяна — {len(live)} на сайта')
    # публичен препис за „Моят профил“ (само вече публикуваното)
    os.makedirs('data', exist_ok=True)
    io.open('data/drivers.json', 'w', encoding='utf-8').write(
        json.dumps(live, ensure_ascii=False, separators=(',', ':')))
    if hidden:
        print('скрити (publish: false):', ', '.join(hidden))


if __name__ == '__main__':
    main()
