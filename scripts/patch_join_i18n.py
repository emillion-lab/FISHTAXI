#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Прикачва преводите към join.html.

Досега страницата беше само на български, без никаква система за
езици.  Тук добавяме id на всеки текстов елемент, падащо меню за
избор, и връзка към lib/join-i18n.js.

Съдържанието на елементите остава българско в самия HTML — то е
резервният вариант, ако скриптът не се зареди.  applyJoinLang()
го подменя веднага при отваряне.
"""
import io, re, sys

PATH = "join.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []


def sub_once(old, new, label, required=True):
    global s
    if new in s:
        report.append(f"{label}: already done")
        return True
    if old in s:
        if s.count(old) != 1:
            raise SystemExit(f"{label}: anchor not unique ({s.count(old)})")
        s = s.replace(old, new, 1)
        report.append(f"{label}: ok")
        return True
    if required:
        raise SystemExit(f"{label}: anchor NOT FOUND")
    report.append(f"{label}: skipped")
    return False


# ── падащо меню за език, най-горе ────────────────────────────────────
sub_once(
 '<div class="brand"><b><span class="fish">fish</span>.taxi</b></div>',
 '<div style="display:flex;justify-content:flex-end;margin-bottom:6px">'
 '<select id="j-lang" aria-label="Language" style="background:#1a1a1a;'
 'color:#ddd;border:1px solid #333;border-radius:8px;padding:6px 10px;'
 'font-size:13px;font-family:inherit"></select></div>\n'
 '  <div class="brand"><b><span class="fish">fish</span>.taxi</b></div>',
 'language selector')

# ── горен текст ──────────────────────────────────────────────────────
sub_once('<p class="lead">Заявка за присъединяване. Отнема по-малко от минута.</p>',
         '<p class="lead" id="j-lead">Заявка за присъединяване. Под минута.</p>',
         'lead')

sub_once('<h1>Първите шофьори не се качват на платформа — основават я.</h1>',
         '<h1 id="j-h1">0% комисиона. Печелиш каквото си изкарал.</h1>',
         'h1')

# параграфът е дълъг — режем по началото и края
m = re.search(r'<p>fish\.taxi тръгва с малка.*?</p>', s, re.S)
if m:
    s = s[:m.start()] + ('<p id="j-p">Големите платформи взимат 20\u201325% от всеки курс. '
                         'Ние не взимаме нищо. Клиентът те вижда, звъни ти директно, '
                         'плаща на теб.</p>') + s[m.end():]
    report.append("intro paragraph: ok")
elif 'id="j-p"' in s:
    report.append("intro paragraph: already done")
else:
    raise SystemExit("intro paragraph: anchor NOT FOUND")

sub_once('<li>Founder значка на профила — постоянна, не изтича</li>',
         '<li id="j-b1">Без комисиона — нито сега, нито по-късно</li>',
         'bullet 1')
sub_once('<li>Приоритетен достъп до нови функции преди всички останали</li>',
         '<li id="j-b2">Клиентът звъни директно на теб</li>',
         'bullet 2')
sub_once('<li>Име в основаването на платформата, каквато и да стане тя</li>',
         '<li id="j-b3">Founder значка за първите — постоянна</li>',
         'bullet 3')

# ── стъпките ─────────────────────────────────────────────────────────
sub_once('<div class="step-n"><i>1</i><span>Твоят телефон</span></div>',
         '<div class="step-n"><i>1</i><span id="j-s1">Твоят телефон</span></div>',
         'step 1 title')
sub_once('<div class="hint" id="phoneHint">Въведи телефонния си номер</div>',
         '<div class="hint" id="phoneHint">Въведи телефонния си номер</div>',
         'phone hint', required=False)

# двете стъпки 2 имат еднакво заглавие — разделяме ги по контекст
sub_once('<div class="step off" id="s2bg">\n      <div class="step-n"><i>2</i><span>Твоят автомобил</span></div>',
         '<div class="step off" id="s2bg">\n      <div class="step-n"><i>2</i><span id="j-s2">Твоят автомобил</span></div>',
         'step 2 (BG) title')
sub_once('<div class="step off" id="s2foreign">\n      <div class="step-n"><i>2</i><span>Твоят автомобил</span></div>',
         '<div class="step off" id="s2foreign">\n      <div class="step-n"><i>2</i><span id="j-s2f">Твоят автомобил</span></div>',
         'step 2 (foreign) title')

sub_once('<div class="hint">Номерът е извън България — колата не е в местния регистър на такситата. Опиши я накратко, ще я потвърдим ръчно.</div>',
         '<div class="hint" id="j-hintF">Колата ще потвърдим ръчно. Опиши я накратко.</div>',
         'foreign hint')

sub_once('<div class="step-n"><i>3</i><span>Твоето име</span></div>',
         '<div class="step-n"><i>3</i><span id="j-s3">Твоето име</span></div>',
         'step 3 title')
sub_once('<div class="step-n"><i>4</i><span>Изпрати заявката</span></div>',
         '<div class="step-n"><i>4</i><span id="j-s4">Изпрати заявката</span></div>',
         'step 4 title')
sub_once('<div class="hint">Отваря се готово съобщение. Само натискаш „изпрати“.</div>',
         '<div class="hint" id="j-hint4">Отваря се готово съобщение. Само натискаш „изпрати“.</div>',
         'step 4 hint')

# ── благодарност ─────────────────────────────────────────────────────
sub_once('<h2 style="margin:14px 0 9px;font-size:1.35rem">Заявката е изпратена</h2>',
         '<h2 id="j-okH" style="margin:14px 0 9px;font-size:1.35rem">Заявката е изпратена</h2>',
         'thanks title')
sub_once('<p style="color:var(--dim);font-size:1rem">Founder статутът те очаква. Ще се свържем с теб до 24 часа.</p>',
         '<p id="j-okP" style="color:var(--dim);font-size:1rem">Ще се свържем с теб до 24 часа.</p>',
         'thanks text')

# ── долният ред: GDPR + бележка за българския регистър ───────────────
m = re.search(r'<div class="foot">.*?</div>', s, re.S)
if m and 'id="j-gdpr"' not in m.group():
    s = s[:m.start()] + (
        '<div class="foot">\n'
        '    <div id="j-gdpr">Показваме на клиентите само това, което сам '
        'попълниш тук. Нищо повече.</div>\n'
        '    <div id="j-footBG" style="margin-top:6px;opacity:.75">За български '
        'номера данните идват от публичния регистър на ИА \u201eАвтомобилна '
        'администрация\u201c.</div>\n'
        '  </div>') + s[m.end():]
    report.append("footer: ok")
elif 'id="j-gdpr"' in s:
    report.append("footer: already done")
else:
    raise SystemExit("footer: anchor NOT FOUND")

# ── скриптът ─────────────────────────────────────────────────────────
if 'lib/join-i18n.js' not in s:
    i = s.find('</head>')
    if i < 0:
        raise SystemExit("</head> not found")
    s = s[:i] + '<script src="lib/join-i18n.js"></script>\n' + s[i:]
    report.append("i18n script linked")
else:
    report.append("i18n script: already linked")

# ── съобщението за грешка при име ────────────────────────────────────
sub_once("'Моля, име и фамилия.'", "(jt().errName||'Please enter your name.')",
         'name error message', required=False)

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
