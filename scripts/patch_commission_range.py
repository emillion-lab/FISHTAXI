#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Коригира процента на комисионата в gen_join_i18n.py.

Беше 20–25%.  Реалността е 20–40% — при кратките курсове делът на
платформата расте, защото минималната такса е фиксирана, а сумата
на курса е малка.  Затова текстът вече казва „до 40%", с изрична
бележка, че при късите курсове е най-зле.
"""
import io, re

PATH = "scripts/gen_join_i18n.py"
s = io.open(PATH, encoding="utf-8").read()
orig = s

NEW_P = {
 'bg': 'Големите платформи взимат 20–40% от всеки курс — при късите най-много. Ние не взимаме нищо. Клиентът те вижда, звъни ти директно, плаща на теб.',
 'en': 'The big platforms take 20–40% of every ride — most on short trips. We take nothing. The client sees you, calls you directly, pays you.',
 'de': 'Die großen Plattformen nehmen 20–40 % pro Fahrt — bei kurzen Strecken am meisten. Wir nehmen nichts. Der Kunde sieht dich, ruft dich direkt an, zahlt an dich.',
 'fr': 'Les grandes plateformes prennent 20 à 40 % de chaque course — le plus sur les trajets courts. Nous, rien. Le client vous voit, vous appelle directement, vous paie.',
 'es': 'Las grandes plataformas se llevan el 20–40 % de cada viaje — más aún en los trayectos cortos. Nosotros, nada. El cliente te ve, te llama directamente y te paga.',
 'it': 'Le grandi piattaforme prendono il 20–40% di ogni corsa — soprattutto sulle tratte brevi. Noi niente. Il cliente ti vede, ti chiama direttamente, paga te.',
 'ru': 'Крупные платформы берут 20–40% с каждой поездки — на коротких больше всего. Мы не берём ничего. Клиент видит вас, звонит напрямую и платит вам.',
 'ro': 'Platformele mari iau 20–40% din fiecare cursă — cel mai mult la cursele scurte. Noi nu luăm nimic. Clientul te vede, te sună direct și îți plătește ție.',
 'el': 'Οι μεγάλες πλατφόρμες παίρνουν 20–40% από κάθε διαδρομή — στις σύντομες ακόμη περισσότερο. Εμείς τίποτα. Ο πελάτης σε βλέπει, σε καλεί απευθείας και σε πληρώνει.',
 'tr': 'Büyük platformlar her yolculuktan %20–40 alır — kısa mesafelerde en çok. Biz hiçbir şey almıyoruz. Müşteri seni görür, doğrudan arar ve sana öder.',
 'pl': 'Duże platformy biorą 20–40% z każdego kursu — na krótkich najwięcej. My nic. Klient cię widzi, dzwoni bezpośrednio i płaci tobie.',
 'nl': 'De grote platforms nemen 20–40% van elke rit — op korte ritten het meest. Wij niets. De klant ziet je, belt je direct en betaalt aan jou.',
}

changed = 0
for code, txt in NEW_P.items():
    # намираме секцията на езика и в нея реда p='...'
    m = re.search(r"'" + code + r"': dict\(", s)
    if not m:
        print(f"  {code}: секция не е намерена")
        continue
    start = m.end()
    nxt = re.search(r"\n'[a-z]{2}': dict\(", s[start:])
    end = start + (nxt.start() if nxt else len(s) - start)
    block = s[start:end]
    pm = re.search(r"\n p='(?:[^'\\]|\\.)*',", block)
    if not pm:
        print(f"  {code}: ред p= не е намерен")
        continue
    if '20–40' in pm.group():
        print(f"  {code}: вече е коригиран")
        continue
    new_line = "\n p=" + repr(txt) + ","
    block = block[:pm.start()] + new_line + block[pm.end():]
    s = s[:start] + block + s[end:]
    changed += 1

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print(f"WRITTEN — {changed} езика коригирани")
