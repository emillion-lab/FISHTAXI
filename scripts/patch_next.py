import io

# Петър -> Петер, нов телефон. gps_id (старият номер без +) остава — по него се свързват логинът и онлайн статусът.
def rep(p):
    s = io.open(p, encoding='utf-8').read()
    n = s.replace('+359897644448', '+359878666671').replace('"Petar M."', '"Peter M."').replace('"Петър М."', '"Петер М."')
    if n == s:
        print('already:', p); return
    io.open(p, 'w', encoding='utf-8').write(n)
    print('ok:', p)

for p in ['data/drivers.json', 'drivers/profiles/petar.json', 'classic.html', 'next/index.html']:
    rep(p)
