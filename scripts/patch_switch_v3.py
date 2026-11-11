#!/usr/bin/env python3
"""Сменя началната страница с новия сайт v3 (11.11.2026).

  index.html (стар сайт)  ->  classic.html  +  backups/index-classic-2026-11-11.html
  app.html (нов сайт)     ->  index.html

Идемпотентен: ако index.html вече е новият сайт, не прави нищо.
Връщане назад: копирай classic.html обратно върху index.html.

ВНИМАНИЕ: след смяната scripts/build_drivers.py трябва да пише DRIVERS в
classic.html (PAGE = 'classic.html'), а driver-intake.yml да добавя classic.html.
Новият сайт чете шофьорите от data/drivers.json и не се нуждае от вграждане.
"""
import io
import os
import shutil
import sys

MARK = 'lib/app-core.js'
OLD_KEY = 'var DRIVERS='
BACKUP = 'backups/index-classic-2026-11-11.html'


def main():
    cur = io.open('index.html', encoding='utf-8').read()
    if MARK in cur:
        print('index.html вече е новият сайт — нищо за правене')
        return
    if cur.count(OLD_KEY) != 1:
        sys.exit('index.html не прилича на стария сайт („var DRIVERS=“ липсва) — спирам')
    if not os.path.exists('app.html'):
        sys.exit('няма app.html — спирам')
    new = io.open('app.html', encoding='utf-8').read()
    if MARK not in new or '</html>' not in new:
        sys.exit('app.html не прилича на новия сайт — спирам')
    for f in ('lib/app.css', 'lib/app-core.js', 'lib/app-ui.js', 'lib/app-order.js', 'data/drivers.json'):
        if not os.path.exists(f):
            sys.exit('липсва ' + f + ' — спирам')
    os.makedirs('backups', exist_ok=True)
    shutil.copyfile('index.html', BACKUP)
    shutil.copyfile('index.html', 'classic.html')
    io.open('index.html', 'w', encoding='utf-8').write(new)
    print('началната страница е новият сайт; старият е на classic.html и в ' + BACKUP)


if __name__ == '__main__':
    main()
