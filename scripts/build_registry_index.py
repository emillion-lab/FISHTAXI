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
"""
import json, os, sys, gzip, collections, datetime, urllib.request

SRC = ('https://raw.githubusercontent.com/emillion-lab/TAXI/main/'
       'Sofia_09.05.2026.json')

def newest_registry():
    """Взима най-новия файл от TAXI вместо да е зашит твърдо."""
    api = 'https://api.github.com/repos/emillion-lab/TAXI/contents/'
    try:
        req = urllib.request.Request(api, headers={'User-Agent': 'fishtaxi'})
        files = json.load(urllib.request.urlopen(req, timeout=60))
        cands = []
        for f in files:
            n = f['name']
            if not n.endswith('.json'):
                continue
            # Sofia_09.05.2026.json  или  taxi_data_Sofia20.07.2026.json
            digits = ''.join(c if c.isdigit() else ' ' for c in n).split()
            if len(digits) >= 3:
                try:
                    d, m, y = int(digits[-3]), int(digits[-2]), int(digits[-1])
                    if y < 100: y += 2000
                    cands.append((datetime.date(y, m, d), f['download_url'], n))
                except ValueError:
                    pass
        if cands:
            cands.sort()
            print('най-нов регистър:', cands[-1][2], cands[-1][0])
            return cands[-1][1]
    except Exception as ex:
        print('не успях да избера най-новия:', ex)
    return SRC

def main():
    url = newest_registry()
    print('тегля', url)
    req = urllib.request.Request(url, headers={'User-Agent': 'fishtaxi'})
    data = json.load(urllib.request.urlopen(req, timeout=300))
    print('оператори в регистъра:', len(data))

    now = datetime.datetime.now(datetime.timezone.utc)
    seen = {}
    for op in data:
        term = op.get('terminationDate')
        if term:
            try:
                if datetime.datetime.fromisoformat(term.replace('Z', '+00:00')) < now:
                    continue          # лицензът е прекратен — колата не е активна
            except ValueError:
                pass
        for v in op.get('vehicles') or []:
            plate = (v.get('registerNumber') or '').replace(' ', '').upper()
            if not plate:
                continue
            seen[plate] = {
                'p': plate,
                'm': (v.get('markAndModel') or '').strip(),
                'o': (op.get('operatorName') or '').strip(),
                'y': (v.get('firstRegistrationDate') or '')[:4],
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
        'v': [[r['p'], mi[r['m']], oi[r['o']],
               int(r['y']) if r['y'].isdigit() else 0] for r in rows],
    }
    os.makedirs('data', exist_ok=True)
    with open('data/registry.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize('data/registry.json')
    gz = len(gzip.compress(open('data/registry.json', 'rb').read()))
    print(f'записан data/registry.json: {size} байта, {gz} след gzip')

if __name__ == '__main__':
    main()
