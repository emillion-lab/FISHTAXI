import io

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s

# ─────────────────────────────────────────────────────────────────────
# QR-ът вече носи vCard, а не само линк.
#
# При сканиране телефонът предлага да запише контакта: име, телефон,
# район на работа, кола и линк към профила (fish.taxi/#d3).
# Работи офлайн — контактът остава в телефона на клиента дори
# без интернет, което е целта на визитката.
#
# Бележки по формата:
#  * vCard 3.0 — най-широко поддържан от Android и iOS
#  * запетаи, точки и запетаи и наклонени черти се екранират
#  * районът се реже до 80 знака, иначе QR-ът става твърде гъст
#  * correctLevel L (не M), защото vCard е доста повече данни от линк
# ─────────────────────────────────────────────────────────────────────

OLD_START = "function renderDriverQR(d){"
i = s.find(OLD_START)
if i < 0:
    raise SystemExit("renderDriverQR not found")

# краят на функцията: първото срещане на затварящата скоба на реда
end_marker = "\n}\n"
j = s.find(end_marker, i)
if j < 0:
    raise SystemExit("end of renderDriverQR not found")
j += len(end_marker)

NEW_FN = '''function vcardEscape(v){
  return String(v==null?'':v)
    .replace(/\\\\/g,'\\\\\\\\')
    .replace(/;/g,'\\\\;')
    .replace(/,/g,'\\\\,')
    .replace(/\\n/g,'\\\\n');
}
/* Визитка на шофьора като vCard — телефонът предлага да я запише
   в контактите: име, телефон, район на работа, кола, линк.        */
function driverVCard(d){
  var name=d.name||('Driver '+d.id);
  var tel=(d.phone||'').replace(/[^0-9+]/g,'');
  if(tel&&tel.charAt(0)!=='+')tel='+'+tel;
  var area=(d.areas||'').replace(/\\s+/g,' ').trim();
  if(area.length>80)area=area.slice(0,77)+'...';
  var car=[d.car,d.plate].filter(Boolean).join(' \\u00b7 ');
  var note=[area,car].filter(Boolean).join(' | ');
  var L=[];
  L.push('BEGIN:VCARD');
  L.push('VERSION:3.0');
  L.push('N:;'+vcardEscape(name)+';;;');
  L.push('FN:'+vcardEscape(name));
  L.push('ORG:fish.taxi');
  if(tel)L.push('TEL;TYPE=CELL:'+tel);
  L.push('URL:'+driverCardUrl(d));
  if(note)L.push('NOTE:'+vcardEscape(note));
  L.push('END:VCARD');
  return L.join('\\n');
}
function renderDriverQR(d){
  var box=document.getElementById('m-qr');
  if(!box)return;
  if(typeof QRCode==='undefined'){box.style.display='none';return;}
  box.innerHTML='';
  try{
    new QRCode(box,{text:driverVCard(d),width:88,height:88,
      colorDark:'#000000',colorLight:'#ffffff',
      correctLevel:QRCode.CorrectLevel.L});
    box.title=(d.name||'')+' \\u2014 '+(d.phone||'');
    box.style.display='block';
  }catch(e){ box.style.display='none'; }
}
'''

if 'function driverVCard' in s:
    print("SKIP: already vCard")
else:
    s = s[:i] + NEW_FN + s[j:]
    print("renderDriverQR -> vCard")

# Копчето вече копира линка към визитката (остава както е), но
# добавяме поясняващ надпис под QR-а, за да е ясно какво прави.
OLD_BTN = ('<button id="m-copylink" onclick="copyDriverLink()" '
           'style="background:none;border:none;color:var(--mu2);font-size:10px;'
           'cursor:pointer;padding:2px 4px">\U0001F517</button>')
NEW_BTN = ('<div style="font-size:9px;color:var(--mu2);text-align:center;'
           'line-height:1.2;max-width:92px">'
           '<span id="m-qr-hint">\u0421\u043a\u0430\u043d\u0438\u0440\u0430\u0439 '
           '\u2192 \u043a\u043e\u043d\u0442\u0430\u043a\u0442</span></div>'
           + OLD_BTN)
if OLD_BTN in s and 'm-qr-hint' not in s:
    s = s.replace(OLD_BTN, NEW_BTN, 1)
    print("hint added under QR")
elif 'm-qr-hint' in s:
    print("hint: already there")
else:
    print("hint: button anchor not found — SKIPPED")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")
