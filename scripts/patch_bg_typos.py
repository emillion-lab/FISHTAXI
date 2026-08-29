#!/usr/bin/env python3
# FT-BG-TYPOS
# Дребни, но видими грешки в bg/ru i18n низовете: остатъчна левова фраза
# след прехода към EUR ("стотинка" -> "цент"), грешна бройна форма за хора
# ("300 шофьора" -> "300 шофьори"), липсваща запетая пред подчинено изречение,
# и същата "стотинка → цент" грешка в руския превод ("копейка" -> "цент").
import io, sys

FILES = ['index.html', 'next/index.html']
MARK = 'FT-BG-TYPOS'

REPLACEMENTS = [
    ('rC4s:" - къде каращ"',
     'rC4s:" - къде караш"'),
    ('rB5s:"Всеки стотинка от курса е твоя. Винаги."',
     'rB5s:"Всеки цент от курса е твой. Винаги."'),
    ('rFree:"БЕЗПЛАТНО за първите 300 шофьора"',
     'rFree:"БЕЗПЛАТНО за първите 300 шофьори"'),
    ('rBeta:"Бета, първите 300 шофьора по света"',
     'rBeta:"Бета, първите 300 шофьори по света"'),
    ('rB4s:"Работиш когато искаш',
     'rB4s:"Работиш, когато искаш'),
    ('кажи ако искаш',
     'кажи, ако искаш'),
    ('paxWarnMsg:"⚠️ 3-4 пътници с багаж — моля потвърдете',
     'paxWarnMsg:"⚠️ 3-4 пътници с багаж — моля, потвърдете'),
    ('не потвърдено возене',
     'а не потвърдено возене'),
    ('rSoon:"Автоматично търсим колата ти в публичния регистър на таксита"',
     'rSoon:"Автоматично търсим колата ти в публичния регистър на такситата"'),
    ('Каждая копейка от поездки ваша',
     'Каждый цент от поездки ваш'),
]

changed = []
for path in FILES:
    try:
        s = io.open(path, encoding='utf-8').read()
    except IOError:
        print('SKIP (липсва): ' + path)
        continue

    if MARK in s:
        print('SKIP (вече е приложено): ' + path)
        continue

    n_done = 0
    for old, new in REPLACEMENTS:
        cnt = s.count(old)
        if cnt == 0:
            print('FAIL: липсва котвата в ' + path + ': ' + old[:50])
            sys.exit(1)
        if cnt > 1:
            print('FAIL: котвата не е уникална (' + str(cnt) + 'x) в ' + path + ': ' + old[:50])
            sys.exit(1)
        s = s.replace(old, new, 1)
        n_done += 1

    marker_anchor = "var T={"
    if marker_anchor not in s:
        print('FAIL: липсва котвата за маркера в ' + path)
        sys.exit(1)
    s = s.replace(marker_anchor, '/* ' + MARK + ' */\nvar T={', 1)

    io.open(path, 'w', encoding='utf-8').write(s)
    changed.append(path + ' (' + str(n_done) + ' поправки)')

print('OK: ' + (', '.join(changed) if changed else 'нищо за промяна'))
