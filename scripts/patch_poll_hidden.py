#!/usr/bin/env python3
"""FT-POLL-HIDDEN-V1 (10.11.2026) — скрит таб не пита /gps.

fish.taxi питаше mvr-proxy /gps на всеки 15 сек, дори когато табът е
скрит или телефонът е заключен. На безплатния Cloudflare план това
изяждаше дневната KV квота и картата с шофьорите изпразваше.

Сега: интервалът пропуска, докато document.hidden; при връщане на таба
картата се опреснява веднага. Идемпотентен. Пипа всяка страница, в която
намери котвата (index.html, next/index.html, indexOLD.html).
"""
import io, sys

OLD = "setInterval(pollGPS,15000);"
NEW = ("/* FT-POLL-HIDDEN-V1: скрит таб не пита /gps — пести KV квотата; при връщане веднага. */\n"
       "setInterval(function(){if(!document.hidden)pollGPS();},15000);\n"
       "document.addEventListener('visibilitychange',function(){if(!document.hidden)pollGPS();});")

changed = 0
for p in ('index.html', 'next/index.html', 'indexOLD.html'):
    try:
        s = io.open(p, encoding='utf-8').read()
    except FileNotFoundError:
        continue
    if 'FT-POLL-HIDDEN-V1' in s:
        print(p, ': вече е приложен')
        continue
    n = s.count(OLD)
    if n != 1:
        print(p, ': котвата е намерена', n, 'пъти — пропускам')
        continue
    io.open(p, 'w', encoding='utf-8').write(s.replace(OLD, NEW))
    changed += 1
    print(p, ': приложен')

if changed == 0:
    print('нищо за промяна')
