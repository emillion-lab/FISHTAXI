#!/usr/bin/env python3
"""Шофьор сам сменя второстепенното (страница „Моят профил“) — 11.11.2026.

Вика се от driver-intake.yml (workflow_dispatch с edit_phone + edit_json).
Автентичността е проверена от mvr-proxy (токен в KV). Тук е втората врата:
само разрешени ключове, само булеви/избрани стойности, никакъв свободен текст.
Не пипа име, снимки, кола, тарифа, био — те минават през Емил.

Употреба: driver_edit.py <телефон> '<json>'
"""
import glob, io, json, re, sys, os

PROFILES = 'drivers/profiles'
BOOL = {'ac', 'music', 'silent_ok', 'talk_ok', 'calm_ok', 'usb', 'streaming',
        'petfriendly', 'childok', 'nosmoker', 'terminal', 'panoroof', 'legroom',
        'music_pop', 'music_chalga', 'music_rock', 'music_classical',
        'music_jazz', 'music_electronic', 'music_chillout', 'music_lounge'}
TRI = {'airport', 'longdist', 'night', 'wheelchair'}      # true / false / "ask"
LANGS = {'bg', 'en', 'ru', 'de', 'fr', 'tr', 'it', 'es'}


def norm(p):
    d = re.sub(r'\D', '', str(p or ''))
    if d.startswith('00'):
        d = d[2:]
    if d.startswith('0'):
        d = '359' + d[1:]
    return d


def main():
    if len(sys.argv) != 3:
        print('употреба: driver_edit.py <телефон> <json>'); return 1
    phone = norm(sys.argv[1])
    try:
        edit = json.loads(sys.argv[2])
        assert isinstance(edit, dict)
    except Exception:
        print('невалиден JSON'); return 1
    target = None
    for path in glob.glob(os.path.join(PROFILES, '*.json')):
        if os.path.basename(path).startswith(('_', 'test-')):
            continue
        p = json.load(io.open(path, encoding='utf-8'))
        if p.get('gps_id') == phone:
            target = (path, p); break
    if not target:
        print('няма профил за този телефон'); return 1
    path, p = target
    changed, skipped = [], []
    for k, v in edit.items():
        if k in BOOL and isinstance(v, bool):
            ok = True
        elif k in TRI and (isinstance(v, bool) or v == 'ask'):
            ok = True
        elif k == 'langs' and isinstance(v, list) and v and set(v) <= LANGS:
            ok = True
        else:
            ok = False
        if not ok:
            skipped.append(k); continue
        if p.get(k) != v:
            p[k] = v; changed.append(k)
    # производни, за да не си противоречат
    if 'music' in edit and isinstance(edit['music'], bool):
        p['nomusic'] = not p['music']
    if 'music_chalga' in edit and isinstance(edit.get('music_chalga'), bool):
        p['chalga'] = p['music_chalga']
    p['smoking'] = False
    if changed:
        io.open(path, 'w', encoding='utf-8').write(json.dumps(p, ensure_ascii=False, indent=1) + '\n')
    print('профил:', os.path.basename(path), '| сменено:', ','.join(changed) or '—',
          '| отхвърлено:', ','.join(skipped) or '—')
    return 0


if __name__ == '__main__':
    sys.exit(main())
