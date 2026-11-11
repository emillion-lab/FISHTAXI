#!/usr/bin/env python3
"""FT-MAP-LOCAL-V1 (11.11.2026): „център на мен“ не вкарва далечни шофьори.

fitBounds събираше потребителя + ВСИЧКИ шофьори → с Lancelot (Сен Тропе)
картата ставаше Европа. Сега влизат само шофьори до 60 км от потребителя;
ако няма такива — картата се центрира на него. Идемпотентен."""
import sys
P = 'index.html'
s = open(P, encoding='utf-8').read()
if 'FT-MAP-LOCAL-V1' in s:
    print('вече е приложен — SKIP'); sys.exit(0)
old = "DRIVERS.forEach(function(d){if(d.lat&&d.lng)pts.push([d.lat,d.lng]);});"
new = "DRIVERS.forEach(function(d){if(d.lat&&d.lng&&haversineKm(userLat,userLng,d.lat,d.lng)<60)pts.push([d.lat,d.lng]);}); /* FT-MAP-LOCAL-V1 */"
if s.count(old) != 1:
    print('котвата не е точно веднъж:', s.count(old)); sys.exit(1)
open(P, 'w', encoding='utf-8').write(s.replace(old, new))
print('FT-MAP-LOCAL-V1: приложен')
