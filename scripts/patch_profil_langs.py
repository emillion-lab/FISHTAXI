#!/usr/bin/env python3
"""profil.html: добавя чешки, арабски, китайски (11.11.2026) — както на сайта.
Без това запазването би махнало cs/ar/zh от профила. Идемпотентен."""
import sys
P = 'profil.html'
s = open(P, encoding='utf-8').read()
old = "['es','Испански']];"
new = "['es','Испански'],['cs','Чешки'],['ar','Арабски'],['zh','Китайски']];"
if new in s:
    print('вече е приложен — SKIP'); sys.exit(0)
if s.count(old) != 1:
    print('котвата не е точно веднъж'); sys.exit(1)
open(P, 'w', encoding='utf-8').write(s.replace(old, new))
print('profil.html: езиците са 11')
