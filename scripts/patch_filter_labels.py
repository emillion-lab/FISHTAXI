#!/usr/bin/env python3
"""FT-FL-LABELS-V1 (11.11.2026): етикетите на филтрите бяха изместени с един ред.

Редовете с филтри са 9, а преведените етикети 8 — липсваше „Стил музика“.
На български излизаше „Комфорт“ до Pop/Rock, „Език“ до „Непушач“ и т.н.
Идемпотентен; котвата трябва да е точно веднъж."""
import sys
P = 'index.html'
s = open(P, encoding='utf-8').read()
if 'FT-FL-LABELS-V1' in s:
    print('вече е приложен — SKIP'); sys.exit(0)
old = "var labels=[t.sStatus,t.sPayment,t.sStyle,t.sCar,t.sAtm,t.sComfort,t.sLang,t.sExtras];"
new = ("var MUS_FL={bg:'Музика',en:'Music Style',de:'Musik',fr:'Musique',ru:'Музыка',it:'Musica',es:'Música'}; /* FT-FL-LABELS-V1 */\n"
       "  var labels=[t.sStatus,t.sPayment,t.sStyle,t.sCar,t.sAtm,t.sMusic||MUS_FL[lang]||MUS_FL.en,t.sComfort,t.sLang,t.sExtras];")
if s.count(old) != 1:
    print('котвата не е точно веднъж:', s.count(old)); sys.exit(1)
open(P, 'w', encoding='utf-8').write(s.replace(old, new))
print('FT-FL-LABELS-V1: етикетите на филтрите са 9')
