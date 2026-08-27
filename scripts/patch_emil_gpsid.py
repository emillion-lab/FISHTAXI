# -*- coding: utf-8 -*-
# FISHTAXI · FT-EMIL-GPSID-V1
#
# Проблем (регресия, разплетена на 27 авг): pollGPS() съпоставя GPS запис
# с профил по String(d.gps_id || d.id). Профилът на Emil няма gps_id, затова
# пада на d.id === 1 и търси driver:1 в KV. Но телефонът на Emil вече праща
# в driver:359878592888. Не съвпадат → профилът стои офлайн и пада на
# hardcode-натия център (lat 42.6977). Петър има gps_id и работи.
#
# Поправка: добавяме gps_id на Emil, точно както е при Петър. Един ключ.
# Идемпотентен: ако вече е добавен, не прави нищо.
import io, sys

p = 'index.html'
s = io.open(p, encoding='utf-8').read()

if '"gps_id":"359878592888"' in s:
    print('SKIP: Emil gps_id вече е добавен')
    sys.exit(0)

OLD = '"id":1,"founder":1,"name":"Emil M."'
NEW = '"id":1,"gps_id":"359878592888","founder":1,"name":"Emil M."'

n = s.count(OLD)
if n != 1:
    print('FAIL: котвата се среща %d пъти, очаква се 1' % n)
    sys.exit(1)

s = s.replace(OLD, NEW)
io.open(p, 'w', encoding='utf-8').write(s)
print('OK: Emil gps_id=359878592888 добавен')
