#!/usr/bin/env python3
"""Маха „🚬 Пушене OK“ от fish.taxi (10.11.2026). Идемпотентен.

Пушенето в такси е забранено — и за пътника, и за шофьора (чл. 56 от Закона
за здравето). Филтърът „Пушене OK“ и значката 🚬 на картата рекламираха
нарушение. Остава само положителният знак 🚭 „Непушач“ — за шофьорите,
които сами са го потвърдили. Без значка = не е потвърдил, нищо повече.

Маха: бутона-филтър, значката 🚬 в списъка и реда 🚬 в картата на шофьора.
Преводите (fSmoking) и клонът на филтъра остават — без бутон са безвредни.
"""
import io, sys

PAGE, MARK = 'index.html', 'FT-NO-SMOKING-OK-V1'
s = io.open(PAGE, encoding='utf-8').read()
if MARK in s:
    print('вече е приложен')
    sys.exit(0)

CUTS = [
    ("\n      <button class=\"flt\" onclick=\"sf('smoking',this)\" data-f='smoking'>🚬 Smoking OK</button>", ''),
    ("\n  if(d.smoking)tags+='<span class=\"t tr\">🚬</span>';",
     "\n  /* " + MARK + ": пушене в такси е забранено — само 🚭 за потвърдилите */"),
    ("[d.smoking,'tr',t.fSmoking],\n    ", ''),
]
for old, new in CUTS:
    n = s.count(old)
    if n != 1:
        sys.exit(f'не намирам точно веднъж ({n}): {old[:60]!r}')
    s = s.replace(old, new)
io.open(PAGE, 'w', encoding='utf-8').write(s)
print('„Пушене OK“ е махнато: филтър, значка, ред в картата')
