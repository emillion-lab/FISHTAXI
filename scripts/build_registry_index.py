#!/usr/bin/env python3
"""Строи лек индекс на таксиметровия регистър за fish.taxi.

Регистърът в TAXI е ~25 MB JSON — не може да се зареди в телефон. Но
същинската информация е малка: 9456 активни таксита, всяко с номер, марка,
модел и оператор. Операторите (276) и моделите (478) се повтарят хиляди
пъти, затова се изнасят в отделни таблици и колите пазят само индекси.

  суров регистър   24.5 MB
  прост индекс      1.0 MB
  с таблици         276 KB
  gzip по мрежата    60 KB   ← това получава телефонът

Изход: registry.json в FISHTAXI, до index.html, за да се тегли от същия домейн.

13.09.2026: TAXI мина на Sofia_YYYY-MM-DD.json.gz. Затова се приемат и .gz,
ISO датата се чете преди D.M.Y, а тихият fallback към твърдо зашит файл е
махнат — ако няма регистър, рънът пада с ясна грешка.
"""
import json, os, re, sys, gzip, collections, datetime, urllib.request


def newest_registry():
    """Взима най-новия софийски файл от TAXI (.json или .json.gz)."""
    api = 'https://api.github.com/repos/emillion-lab/TAXI/contents/'
    req = urllib.request.Request(api, headers={'User-Agent': 'fishtaxi'})
    files = json.load(urllib.request.urlopen(req, timeout=60))
    cands = []
    for f in files:
        n = f['name']
        if 'Sofia' not in n or not n.endswith(('.json', '.json.gz')):
            continue
        # Sofia_2026-09-01.json.gz  — ISO първо
        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', n)
        if m:
            y, mo, d = map(int, m.groups())
        else:
            # Sofia_09.05.2026.json  или  taxi_data_Sofia20.07.2026.json
            m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', n)
            if not m:
                continue
            d, mo, y = map(int, m.groups())
        try:
            cands.append((datetime.date(y, mo, d), f['download_url'], n))
        except ValueError:
            pass
    if not cands:
        sys.exit('няма софийски регистър в TAXI')
    cands.sort()
    print('най-нов регистър:', cands[-1][2], cands[-1][0])
    return cands[-1][1]


def main():
    url = newest_registry()
    print('тегля', url)
    req = urllib.request.Request(url, headers={'User-Agent': 'fishtaxi'})
    raw = urllib.request.urlopen(req, timeout=300).read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    data = json.loads(raw)
    print('оператори в регистъра:', len(data))

    now = datetime.datetime.now(datetime.timezone.utc)

    def parse(s):
        try:
            return datetime.datetime.fromisoformat((s or '').replace('Z', '+00:00'))
        except ValueError:
            return None

    seen = {}
    for op in data:
        term = parse(op.get('terminationDate'))
        if term and term < now:
            continue                  # лицензът е прекратен — колата не е активна

        # валидност на лиценза, по регистрационен номер
        valid = {}
        for tl in op.get('taxiLicensesVehiclesDrivers') or []:
            veh = tl.get('taxiLicenseVehicle') or {}
            lic = tl.get('taxiLicense') or {}
            pl = (veh.get('registerNumber') or '').replace(' ', '').upper()
            vt = (lic.get('validTo') or '')[:10]
            # една кола има по няколко лиценза през годините — взема се последният
            if pl and vt and vt > valid.get(pl, ''):
                valid[pl] = vt

        n_drivers = len([x for x in (op.get('drivers') or []) if x.get('driverName')])
        n_vehicles = len(op.get('vehicles') or [])

        for v in op.get('vehicles') or []:
            plate = (v.get('registerNumber') or '').replace(' ', '').upper()
            if not plate:
                continue
            seen[plate] = {
                'p': plate,
                'm': (v.get('markAndModel') or '').strip(),
                'o': (op.get('operatorName') or '').strip(),
                'y': (v.get('firstRegistrationDate') or '')[:4],
                'to': valid.get(plate, ''),
                'nd': n_drivers,
                'nv': n_vehicles,
            }

    rows = sorted(seen.values(), key=lambda r: r['p'])
    print('активни таксита:', len(rows))
    if len(rows) < 1000:
        print('ПОДОЗРИТЕЛНО МАЛКО — не презаписвам'); sys.exit(1)

    ops = [o for o, _ in collections.Counter(r['o'] for r in rows).most_common()]
    mods = [m for m, _ in collections.Counter(r['m'] for r in rows).most_common()]
    oi = {o: i for i, o in enumerate(ops)}
    mi = {m: i for i, m in enumerate(mods)}

    out = {
        'generated': datetime.date.today().isoformat(),
        'source': url.rsplit('/', 1)[-1],
        'ops': ops, 'mods': mods,
        # [номер, модел, оператор, година, валиден до, брой шофьори, брой возила]
        'v': [[r['p'], mi[r['m']], oi[r['o']],
               int(r['y']) if r['y'].isdigit() else 0,
               r['to'], r['nd'], r['nv']] for r in rows],
    }
    os.makedirs('data', exist_ok=True)
    with open('data/registry.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize('data/registry.json')
    gz = len(gzip.compress(open('data/registry.json', 'rb').read()))
    print(f'записан data/registry.json: {size} байта, {gz} след gzip')

if __name__ == '__main__':
    main()
