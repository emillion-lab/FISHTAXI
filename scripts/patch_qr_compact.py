import io

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s

# ─────────────────────────────────────────────────────────────────────
# Библиотеката qrcodejs поддържа само до тип 10 (макс. ~271 байта при
# ниво L).  Предишният vCard включваше пълния район на работа, който при
# Lancelot е дълъг и съдържа тире-em, средна точка и екранирани запетаи.
# UTF-8 ги брои по 2-3 байта, така че 268 ЗНАКА ставаха 3836 бита и
# конструкторът хвърляше "code length overflow".
#
# Затова:
#  * районът излиза от QR-а — вижда се на самата страница така или иначе
#  * не-ASCII знаци се заменят с ASCII еквиваленти
#  * общата дължина се проверява и при нужда се реже до безопасното
# ─────────────────────────────────────────────────────────────────────

OLD_START = "function driverVCard(d){"
i = s.find(OLD_START)
if i < 0:
    raise SystemExit("driverVCard not found")
j = s.find("\n}\n", i)
if j < 0:
    raise SystemExit("end of driverVCard not found")
j += len("\n}\n")

NEW_FN = '''function asciiFold(v){
  return String(v==null?'':v)
    .replace(/[\\u2010-\\u2015]/g,'-')     /* тирета */
    .replace(/[\\u2018\\u2019]/g,"'")
    .replace(/[\\u201C\\u201D]/g,'"')
    .replace(/\\u00b7/g,'-')              /* средна точка */
    .replace(/\\u2026/g,'...')
    .replace(/\\s+/g,' ')
    .trim();
}
/* Визитка като vCard.  Пази се КРАТКА нарочно: библиотеката побира
   само ~270 байта, а кирилица и типографски знаци заемат по 2-3.
   Районът съзнателно не влиза — вижда се на самата страница.      */
function driverVCard(d){
  var name=asciiFold(d.name||('Driver '+d.id));
  var tel=(d.phone||'').replace(/[^0-9+]/g,'');
  if(tel&&tel.charAt(0)!=='+')tel='+'+tel;
  var car=asciiFold([d.car,d.plate].filter(Boolean).join(' '));
  var L=[];
  L.push('BEGIN:VCARD');
  L.push('VERSION:3.0');
  L.push('N:;'+vcardEscape(name)+';;;');
  L.push('FN:'+vcardEscape(name));
  L.push('ORG:fish.taxi');
  if(tel)L.push('TEL;TYPE=CELL:'+tel);
  L.push('URL:'+driverCardUrl(d));
  if(car)L.push('NOTE:'+vcardEscape(car));
  L.push('END:VCARD');
  var out=L.join('\\n');
  /* последна защита: ако пак е твърде дълго, махаме NOTE */
  if(out.length>230){
    L=L.filter(function(x){return x.indexOf('NOTE:')!==0;});
    out=L.join('\\n');
  }
  return out;
}
'''

if 'function asciiFold' in s:
    print("SKIP: already compacted")
else:
    s = s[:i] + NEW_FN + s[j:]
    print("driverVCard compacted (area removed, ascii-folded)")

# Ако QR-ът все пак не се побере — показваме причината, вместо да мълчим.
OLD_CATCH = "}catch(e){ box.style.display='none'; }"
NEW_CATCH = ("}catch(e){ box.style.display='block';"
             "box.innerHTML='<span style=\"font-size:9px;color:#c00\">QR: '"
             "+(e&&e.message?e.message:'error')+'</span>'; }")
if OLD_CATCH in s:
    s = s.replace(OLD_CATCH, NEW_CATCH, 1)
    print("silent catch -> visible error")
elif "QR: '" in s:
    print("visible catch: already there")
else:
    print("catch anchor not found - SKIPPED")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")
