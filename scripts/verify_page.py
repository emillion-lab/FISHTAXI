# -*- coding: utf-8 -*-
# Проверка на целостта на страница след патч.
# Употреба: python3 scripts/verify_page.py next/index.html [/tmp/inline.js]
#
# Извадено в отделен файл нарочно: Python с ъглови скоби вътре в YAML
# block scalar чупи workflow-а тихо (името му става пътя на файла).
import io, re, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
jsout = sys.argv[2] if len(sys.argv) > 2 else '/tmp/inline.js'

s = io.open(path, encoding='utf-8').read()
ok = True

def check(cond, msg):
    global ok
    print(('OK      ' if cond else 'ГРЕШКА  ') + msg)
    if not cond:
        ok = False

open_tag = '<' + 'style>'
close_tag = '</' + 'style>'
marker = 'FT-M3-V2'

check(s.count(open_tag) == 1 and s.count(close_tag) == 1, 'един стилов блок')
check(marker in s, 'патчът е вътре')
check('</' + 'body>' in s, 'body е затворен')
check(len(s) > 100000, 'файлът не е отрязан (%d знака)' % len(s))

o = len(re.findall(r'<div', s))
c = len(re.findall(r'</' + r'div>', s))
check(o == c, 'баланс на div: %d отворени / %d затворени' % (o, c))

if marker in s:
    css = s.split(marker)[1].split(close_tag)[0]
    check(css.count('{') == css.count('}'),
          'скобите в новия CSS са балансирани (%d / %d)' % (css.count('{'), css.count('}')))

blocks = re.findall(r'<' + r'script>(.*?)</' + r'script>', s, re.S)
check(len(blocks) > 0, 'има вграден JavaScript (%d блока)' % len(blocks))
if blocks:
    io.open(jsout, 'w', encoding='utf-8').write(max(blocks, key=len))
    print('        най-големият JS блок записан в %s' % jsout)

sys.exit(0 if ok else 1)
