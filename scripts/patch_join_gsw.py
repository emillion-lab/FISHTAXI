#!/usr/bin/env python3
"""FT-JOIN-GSW-V1 (17.11.2026): швейцарски немски (gsw) за join.html.

Езиците на join.html живеят в scripts/gen_join_i18n.py, така че пачваме генератора и
пускаме наново lib/join-i18n.js. Самият генератор не се коммитва от apply-patch
(няма го в `git add`), затова го добавяме на ръка със `git add`.
Идемпотентен; всяка котва трябва да е точно веднъж."""
import io, os, subprocess, sys

G = 'scripts/gen_join_i18n.py'
OUT = 'lib/join-i18n.js'

GSW = dict(
 lead='Aamäldig als Fahrer. Under ere Minute.',
 h1='0 % Kommission. Du behaltsch, was du verdienisch.',
 p='D grosse Plattforme nämed 20–40 % vo jedere Fahrt – bi churze Strecke am meiste. Mir nämed nüt. De Chund gseht dich, rüeft dich diräkt aa und zahlt dir.',
 b1='Kei Kommission – nöd jetzt und nöd spöter',
 b2='D Chunde rüefed dich diräkt aa',
 b3='Founder-Abzeiche für die Erschte – dauerhaft',
 s1='Dini Telefonnummere', ph1='Telefon', hint1='Gib dini Telefonnummere ii',
 s2='Din Wage', ph2='Nummereschild', hint2='Gib mindestens 3 Zeiche ii',
 hintF='Mir prüefed s Auto vo Hand. Beschriib es churz.', phF='Marke, Modell, Nummere',
 s3='Din Name', ph3='Vor- und Nachname',
 s4='Aafrag schicke', hint4='E fertigi Nachricht gaht uf. Du drücksch nume uf Sende.',
 okH='Aafrag gschickt', okP='Mir mäldid is innerhalb vo 24 Stunde.',
 errName='Bitte Vor- und Nachname aagäh.',
 gdpr='Mir zeiged de Chunde nume, was du da iigisch. Süsch nüt.',
 footBG='',
)

def one(s, old, new, what):
    n = s.count(old)
    if n != 1:
        print('котвата "%s" не е точно веднъж: %d' % (what, n)); sys.exit(1)
    return s.replace(old, new)

s = io.open(G, encoding='utf-8').read()
if "'gsw'" in s:
    print(G, ': вече има gsw — SKIP генератора')
else:
    s = one(s, "LANGS = ['bg','en','de','fr',", "LANGS = ['bg','en','de','gsw','fr',", 'LANGS')
    s = one(s, "'de':'Deutsch','fr':'Français',", "'de':'Deutsch','gsw':'Schwiizerdütsch','fr':'Français',", 'NAMES')
    entry = "'gsw': dict(\n" + ''.join(' %s=%r,\n' % (k, v) for k, v in GSW.items()) + '),\n'
    s = one(s, "\n'fr': dict(\n", "\n" + entry + "'fr': dict(\n", 'T')
    io.open(G, 'w', encoding='utf-8', newline='').write(s)
    print(G, ': gsw добавен')

# нов lib/join-i18n.js от генератора (проверката за липсващи ключове е в него)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, G], capture_output=True, text=True, encoding='utf-8', env=env)
if r.returncode != 0 or not r.stdout.strip():
    print('генераторът падна:', r.stderr); sys.exit(1)
io.open(OUT, 'w', encoding='utf-8', newline='').write(r.stdout)
print(OUT, ': прегенериран,', len(r.stdout), 'байта')

# генераторът не е в `git add` на workflow-а
subprocess.run(['git', 'add', G], check=True)
print('FT-JOIN-GSW-V1 готово')
