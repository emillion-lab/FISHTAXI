"""Добавя валидност на лиценза и брой шофьори към индекса.

Регистърът носи повече, отколкото ползвахме: в taxiLicensesVehiclesDrivers
всяка кола е вързана за лиценз с validTo, а операторът има поименен списък
с шофьори (3335 общо). Показването им при регистрация върши двойна работа —
шофьорът вижда, че данните му вече са известни, и че лицензът му е проверен.

  7201 от 9456 коли имат дата на валидност
  gzip остава 67 KB
"""
import io

src = io.open('scripts/build_registry_index.py', encoding='utf-8').read()
count = 0

def rep(old, new):
    global src, count
    c = src.count(old)
    assert c == 1, 'MARKER x%d: %r' % (c, old[:70])
    src = src.replace(old, new); count += 1

rep("""    now = datetime.datetime.now(datetime.timezone.utc)
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
            }""",
"""    now = datetime.datetime.now(datetime.timezone.utc)

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
            if pl and lic.get('validTo'):
                valid[pl] = lic['validTo'][:10]

        n_drivers = len([x for x in (op.get('drivers') or []) if x.get('driverName')])

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
            }""")

rep("""        'v': [[r['p'], mi[r['m']], oi[r['o']],
               int(r['y']) if r['y'].isdigit() else 0] for r in rows],""",
"""        # [номер, модел, оператор, година, валиден до, брой шофьори]
        'v': [[r['p'], mi[r['m']], oi[r['o']],
               int(r['y']) if r['y'].isdigit() else 0,
               r['to'], r['nd']] for r in rows],""")

io.open('scripts/build_registry_index.py', 'w', encoding='utf-8').write(src)
print('PATCHED %d blocks OK' % count)
