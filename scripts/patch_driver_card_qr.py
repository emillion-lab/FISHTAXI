import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# 0. БЪГФИКС: openMod получава id (число), а buildPaxOptions очаква
#    обекта на шофьора. Заради това менюто с местата винаги падаше на 4.
# ─────────────────────────────────────────────────────────────────────
OLD_CALL = ("function openMod(id){\n  buildPaxOptions(id);\n"
            "  cur=DRIVERS.filter(function(d){return d.id===id;})[0];\n"
            "  if(!cur)return;")
NEW_CALL = ("function openMod(id){\n"
            "  cur=DRIVERS.filter(function(d){return d.id===id;})[0];\n"
            "  if(!cur)return;\n"
            "  buildPaxOptions(cur);\n"
            "  renderDriverQR(cur);\n"
            "  try{location.hash='d'+cur.id;}catch(e){}")
if OLD_CALL in s:
    s = s.replace(OLD_CALL, NEW_CALL, 1)
    report.append("BUGFIX: buildPaxOptions received id instead of driver object")
elif "buildPaxOptions(cur);" in s:
    report.append("openMod: already patched")
else:
    raise SystemExit("openMod head anchor not found")

# ─────────────────────────────────────────────────────────────────────
# 1. QR библиотека — рисува се в браузъра, без файлове с картинки
# ─────────────────────────────────────────────────────────────────────
QR_LIB = ('<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/'
          'qrcode.min.js"></script>\n')
if 'qrcodejs' not in s:
    i = s.find('</head>')
    if i < 0:
        raise SystemExit("</head> not found")
    s = s[:i] + QR_LIB + s[i:]
    report.append("QR library added")
else:
    report.append("QR library: already there")

# ─────────────────────────────────────────────────────────────────────
# 2. Визитка: собствен линк на всеки шофьор + QR
# ─────────────────────────────────────────────────────────────────────
HELPER = '''
/* ── Визитка на шофьор ────────────────────────────────────────────
   Всеки шофьор има собствен линк: fish.taxi/#d3
   QR кодът до аватара води точно към него — шофьорът може да го
   покаже на клиент или да си го залепи на стъклото. Рисува се в
   браузъра, без файлове с картинки.                                */
function driverCardUrl(d){
  return location.origin+location.pathname+'#d'+d.id;
}
function renderDriverQR(d){
  var box=document.getElementById('m-qr');
  if(!box)return;
  if(typeof QRCode==='undefined'){box.style.display='none';return;}
  box.innerHTML='';
  try{
    new QRCode(box,{text:driverCardUrl(d),width:70,height:70,
      colorDark:'#000000',colorLight:'#ffffff',
      correctLevel:QRCode.CorrectLevel.M});
    box.title=driverCardUrl(d);
    box.style.display='block';
  }catch(e){ box.style.display='none'; }
}
function copyDriverLink(){
  if(!cur)return;
  var url=driverCardUrl(cur);
  var done=function(){
    var b=document.getElementById('m-copylink');
    if(!b)return;
    var old=b.textContent;
    b.textContent='\\u2713';
    setTimeout(function(){b.textContent=old;},1400);
  };
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(url).then(done,done);
  }else{
    var ta=document.createElement('textarea');
    ta.value=url;document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy');}catch(e){}
    document.body.removeChild(ta);done();
  }
}
/* Отваряне по линк: fish.taxi/#d3 показва профила директно. */
function openFromHash(){
  var m=/^#d(\\d+)$/.exec(location.hash||'');
  if(!m)return;
  var id=parseInt(m[1],10);
  if(DRIVERS.filter(function(d){return d.id===id;}).length)openMod(id);
}
window.addEventListener('hashchange',function(){
  if(location.hash)openFromHash();
});
'''

if 'function driverCardUrl' not in s:
    anchor = 'function buildPaxOptions('
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("buildPaxOptions anchor not found")
    s = s[:i] + HELPER.lstrip('\n') + '\n' + s[i:]
    report.append("driver card helpers added")
else:
    report.append("driver card helpers: already there")

# ─────────────────────────────────────────────────────────────────────
# 3. Чистим hash при затваряне
# ─────────────────────────────────────────────────────────────────────
m = re.search(r'function closeMod\(\)\s*\{', s)
if m and 'history.replaceState' not in s[m.end():m.end()+220]:
    ins = m.end()
    s = (s[:ins] +
         "\n  try{history.replaceState(null,'',location.pathname"
         "+location.search);}catch(e){}" + s[ins:])
    report.append("closeMod clears hash")
else:
    report.append("closeMod hash cleanup: already there")

# ─────────────────────────────────────────────────────────────────────
# 4. Слот за QR до аватара.  Аватарът е <div class="mav" id="mav">
# ─────────────────────────────────────────────────────────────────────
if 'id="m-qr"' not in s:
    OLD_AV = '<div class="mav" id="mav">\U0001F697</div>'
    if OLD_AV not in s:
        raise SystemExit("mav avatar div not found")
    NEW_AV = ('<div style="display:flex;align-items:center;justify-content:center;'
              'gap:14px;flex-wrap:wrap">'
              + OLD_AV +
              '<div style="display:flex;flex-direction:column;align-items:center;'
              'gap:2px">'
              '<div id="m-qr" style="background:#fff;padding:5px;border-radius:8px;'
              'line-height:0"></div>'
              '<button id="m-copylink" onclick="copyDriverLink()" '
              'style="background:none;border:none;color:var(--mu2);font-size:10px;'
              'cursor:pointer;padding:2px 4px">\U0001F517</button>'
              '</div></div>')
    s = s.replace(OLD_AV, NEW_AV, 1)
    report.append("QR slot added next to avatar")
else:
    report.append("QR slot: already there")

# ─────────────────────────────────────────────────────────────────────
# 5. При зареждане — ако линкът е #d3, отваряме профила
# ─────────────────────────────────────────────────────────────────────
if 'setTimeout(openFromHash' not in s:
    m = re.search(r'\n(\s*)(renderDrivers\(\);|renderList\(\);|drawList\(\);)', s)
    if m:
        j = m.end()
        s = s[:j] + "\n" + m.group(1) + "setTimeout(openFromHash,350);" + s[j:]
        report.append("openFromHash called on load")
    else:
        report.append("load hook: render call not found — SKIPPED")
else:
    report.append("openFromHash on load: already there")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
