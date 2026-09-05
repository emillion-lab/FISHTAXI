import io

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s

# ─────────────────────────────────────────────────────────────────────
# vCard-ът вътре в QR остава ЧИСТО ASCII, винаги.
#
# Защо: кодирането на не-ASCII знаци във vCard не е еднакво между
# Android, iOS и по-старите четци.  Чужд клиент, който сканира визитка
# с кирилица, рискува да види йероглифи вместо име.  Латиницата се
# чете еднакво навсякъде.
#
# Днес имената в базата са на латиница и това работи по случайност.
# Транслитерацията го прави гарантирано за всеки бъдещ шофьор.
#
# Забележка: това важи САМО за съдържанието на QR кода.  На самата
# страница имената и районите си остават на кирилица както преди.
# ─────────────────────────────────────────────────────────────────────

OLD_START = "function asciiFold(v){"
i = s.find(OLD_START)
if i < 0:
    raise SystemExit("asciiFold not found")
j = s.find("\n}\n", i)
if j < 0:
    raise SystemExit("end of asciiFold not found")
j += len("\n}\n")

NEW_FN = '''var CYR2LAT={
 '\\u0430':'a','\\u0431':'b','\\u0432':'v','\\u0433':'g','\\u0434':'d','\\u0435':'e','\\u0436':'zh',
 '\\u0437':'z','\\u0438':'i','\\u0439':'y','\\u043a':'k','\\u043b':'l','\\u043c':'m','\\u043d':'n',
 '\\u043e':'o','\\u043f':'p','\\u0440':'r','\\u0441':'s','\\u0442':'t','\\u0443':'u','\\u0444':'f',
 '\\u0445':'h','\\u0446':'ts','\\u0447':'ch','\\u0448':'sh','\\u0449':'sht','\\u044a':'a',
 '\\u044c':'y','\\u044e':'yu','\\u044f':'ya','\\u044d':'e','\\u0451':'e','\\u044b':'y','\\u0449':'sht'
};
function translit(v){
  var out='';
  for(var i=0;i<v.length;i++){
    var ch=v.charAt(i), low=ch.toLowerCase(), rep=CYR2LAT[low];
    if(rep){
      /* пазим главната буква, ако оригиналът е бил главен */
      out += (ch!==low) ? rep.charAt(0).toUpperCase()+rep.slice(1) : rep;
    } else {
      out += ch;
    }
  }
  return out;
}
/* QR-ът носи само ASCII: кодирането на кирилица не е еднакво между
   Android, iOS и старите четци, а визитката трябва да се чете от
   чужди клиенти без изненади.                                     */
function asciiFold(v){
  var t=translit(String(v==null?'':v))
    .replace(/[\\u2010-\\u2015]/g,'-')
    .replace(/[\\u2018\\u2019]/g,"'")
    .replace(/[\\u201C\\u201D]/g,'"')
    .replace(/\\u00b7/g,'-')
    .replace(/\\u2026/g,'...')
    .replace(/\\u00a0/g,' ');
  /* каквото е останало извън ASCII, отпада — по-добре липсва,
     отколкото да се покаже като въпросителни на чужд телефон */
  t=t.replace(/[^\\x20-\\x7E]/g,'');
  return t.replace(/\\s+/g,' ').trim();
}
'''

if 'function translit' in s:
    print("SKIP: transliteration already there")
else:
    s = s[:i] + NEW_FN + s[j:]
    print("asciiFold now transliterates Cyrillic and strips non-ASCII")

# Името във vCard-а също минава през asciiFold (вече го прави),
# но се уверяваме, че и FN/N ползват сгънатата версия.
if 'var name=asciiFold(' not in s:
    OLD_NAME = "var name=d.name||('Driver '+d.id);"
    NEW_NAME = "var name=asciiFold(d.name||('Driver '+d.id));"
    if OLD_NAME in s:
        s = s.replace(OLD_NAME, NEW_NAME, 1)
        print("name now ascii-folded")
else:
    print("name folding: already there")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")
