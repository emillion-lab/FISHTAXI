import io

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s

# ─────────────────────────────────────────────────────────────────────
# vCard-ът в QR остава чист ASCII.
#
# Имената на шофьорите се въвеждат на латиница по правило, затова
# транслитерация не е нужна — тя произвеждаше безсмислици за марки
# коли ("Октавия" -> "Oktaviya" вместо Octavia) и градове
# ("София" -> "Sofiya" вместо Sofia).
#
# Остава само сгъването на типографски знаци, което беше истинската
# причина за "code length overflow": тире-em и средна точка заемат
# по 3 байта в UTF-8 вместо 1.
#
# Ако някой ден попадне не-ASCII знак, той отпада тихо — по-добре
# липсва, отколкото да се покаже като въпросителни на чужд телефон.
# ─────────────────────────────────────────────────────────────────────

# Махаме таблицата и функцията за транслитерация, ако са налични.
i = s.find("var CYR2LAT={")
if i >= 0:
    j = s.find("function asciiFold(v){", i)
    if j < 0:
        raise SystemExit("asciiFold not found after CYR2LAT")
    s = s[:i] + s[j:]
    print("removed CYR2LAT table and translit()")
else:
    print("translit: not present")

# Заменяме тялото на asciiFold с версия без транслитерация.
i = s.find("function asciiFold(v){")
if i < 0:
    raise SystemExit("asciiFold not found")
j = s.find("\n}\n", i)
if j < 0:
    raise SystemExit("end of asciiFold not found")
j += len("\n}\n")

NEW_FN = '''/* Сгъва типографските знаци до ASCII.  Имената се въвеждат на
   латиница по правило, затова тук няма транслитерация — марки и
   градове имат истинско латинско изписване, а буква по буква
   излиза безсмислица.                                          */
function asciiFold(v){
  var t=String(v==null?'':v)
    .replace(/[\\u2010-\\u2015]/g,'-')
    .replace(/[\\u2018\\u2019]/g,"'")
    .replace(/[\\u201C\\u201D]/g,'"')
    .replace(/\\u00b7/g,'-')
    .replace(/\\u2026/g,'...')
    .replace(/\\u00a0/g,' ')
    .replace(/[^\\x20-\\x7E]/g,'');
  return t.replace(/\\s+/g,' ').trim();
}
'''

if 'translit(' in s[i:j]:
    s = s[:i] + NEW_FN + s[j:]
    print("asciiFold simplified (no transliteration)")
elif 'no transliteration' in s[i:j] or 'няма транслитерация' in s[i:j]:
    print("asciiFold: already simplified")
else:
    s = s[:i] + NEW_FN + s[j:]
    print("asciiFold replaced")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")
