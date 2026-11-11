#!/usr/bin/env python3
"""Пробна страница v2.html = index.html + индустриалният слой (11.11.2026).

Живият index.html НЕ се пипа. v2.html се сглобява наново при всяко пускане:
копие на index.html + шрифтове + lib/ind.css + lib/ind.js + знак „ПРОБА“.
Версията в адреса (?v=) е от съдържанието на файловете — нова редакция
на слоя = нов адрес = телефонът не държи старото в кеша.

С --live същото отива в index.html (без знака и без noindex) — само след
„да“ от Емил. Идемпотентно: ако слоят вече е вътре, не се слага втори път.
"""
import hashlib, io, sys

LIVE = '--live' in sys.argv
SRC, OUT = 'index.html', ('index.html' if LIVE else 'v2.html')
MARK = '<!-- FT-INDUSTRIAL-V1 -->'


def ver(path):
    return hashlib.sha1(io.open(path, 'rb').read()).hexdigest()[:8]


s = io.open(SRC, encoding='utf-8').read()
if MARK in s:
    if LIVE:
        print('слоят вече е в index.html — SKIP'); sys.exit(0)
    print('index.html вече съдържа слоя — v2.html не е нужен'); sys.exit(1)
for tag in ('</head>', '</body>'):
    if s.count(tag) != 1:
        print(f'{tag} не е точно веднъж в {SRC}'); sys.exit(1)

head = (MARK + '\n'
        + ('' if LIVE else '<meta name="robots" content="noindex">\n')
        + '<link rel="preconnect" href="https://fonts.googleapis.com">'
          '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600'
          '&family=IBM+Plex+Sans+Condensed:wght@500;600;700&display=swap">\n'
        + f'<link rel="stylesheet" href="lib/ind.css?v={ver("lib/ind.css")}">\n')
body = (('' if LIVE else '<div id="ind-preview">ПРОБА · v2</div>\n')
        + f'<script src="lib/ind.js?v={ver("lib/ind.js")}"></script>\n')

s = s.replace('</head>', head + '</head>').replace('</body>', body + '</body>')
io.open(OUT, 'w', encoding='utf-8').write(s)
print(f'{OUT}: слоят е сложен (css {ver("lib/ind.css")}, js {ver("lib/ind.js")})')
