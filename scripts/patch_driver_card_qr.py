import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# 0. БЪГФИКС: openMod получава id (число), а buildPaxOptions очаква
#    обекта на шофьора. Заради това менюто с местата винаги падаше на 4.
# ─────────────────────────────────────────────────────────────────────
OLD_CALL = "function openMod(id){\n  buildPaxOptions(id);\n  cur=DRIVERS.filter(function(d){return d.id===id;})[0];\n  if(!cur)return;"
NEW_CALL = ("function openMod(id){\n"
            "  cur=DRIVERS.filter(function(d){return d.id===id;})[0];\n"
            "  if(!cur)return;\n"
            "  buildPaxOptions(cur);\n"
            "  location.hash='d'+cur.id;")
if OLD_CALL in s:
    s = s.replace(OLD_CALL, NEW_CALL, 1)
    report.append("BUGFIX: buildPaxOptions got id instead of driver object")
elif "buildPaxOptions(cur);" in s:
    report.append("buildPaxOptions fix: already done")
else:
    raise SystemExit("openMod head anchor not found")

# ─────────────────────────────────────────────────────────────────────
# 1. QR библиотека (рисува се в браузъра — никакви файлове с картинки)
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
# 2. Визитка: deep link + QR до аватара
# ─────────────────────────────────────────────────────────────────────
HELPER = '''
/* ── Визитка на шофьор ────────────────────────────────────────────
   Всеки шофьор има собствен линк: fish.taxi/#d3
   QR кодът до аватара води точно към него — шофьорът може да го
   покаже на клиент или да си го сложи на стъклото. Рисува се в
   браузъра, без файлове с картинки.                                */
function driverCardUrl(d){
  return location.origin+location.pathname+'#d'+d.id;
}
function renderDriverQR(d){
  var box=document.getElementById('m-qr');
  if(!box||typeof QRCode==='undefined')return;
  box.innerHTML='';
  try{
    new QRCode(box,{text:driverCardUrl(d),width:74,height:74,
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
  if(!location.hash)return;
  openFromHash();
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
# 3. Рисуваме QR при отваряне на профил
# ─────────────────────────────────────────────────────────────────────
if 'renderDriverQR(cur)' not in s:
    anchor = "  buildPaxOptions(cur);"
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("buildPaxOptions(cur) anchor not found")
    j = i + len(anchor)
    s = s[:j] + "\n  renderDriverQR(cur);" + s[j:]
    report.append("renderDriverQR hooked into openMod")
else:
    report.append("renderDriverQR hook: already there")

# ─────────────────────────────────────────────────────────────────────
# 4. Чистим hash при затваряне, за да не заяжда при следващо отваряне
# ─────────────────────────────────────────────────────────────────────
m = re.search(r'function closeMod\(\)\s*\{', s)
if m and 'history.replaceState' not in s[m.end():m.end()+220]:
    ins = m.end()
    s = (s[:ins] +
         "\n  try{history.replaceState(null,'',location.pathname"
         "+location.search);}catch(e){}" + s[ins:])
    report.append("closeMod clears hash")
else:
    report.append("closeMod hash cleanup: already there or not found")

# ─────────────────────────────────────────────────────────────────────
# 5. Слот за QR до аватара в модала
# ─────────────────────────────────────────────────────────────────────
if 'id="m-qr"' not in s:
    m = re.search(r'<img[^>]*id="m-av"[^>]*>', s)
    if not m:
        raise SystemExit("m-av avatar element not found")
    block = ('<div style="display:flex;align-items:center;justify-content:center;'
             'gap:14px;flex-wrap:wrap">'
             + m.group() +
             '<div style="display:flex;flex-direction:column;align-items:center;gap:3px">'
             '<div id="m-qr" style="background:#fff;padding:5px;border-radius:8px;'
             'line-height:0"></div>'
             '<button id="m-copylink" onclick="copyDriverLink()" '
             'style="background:none;border:none;color:var(--mu2);font-size:10px;'
             'cursor:pointer;padding:2px 4px" title="Copy link">\U0001F517</button>'
             '</div></div>')
    s = s[:m.start()] + block + s[m.end():]
    report.append("QR slot added next to avatar")
else:
    report.append("QR slot: already there")

# ─────────────────────────────────────────────────────────────────────
# 6. При зареждане на страницата — ако има #d3, отваряме профила
# ─────────────────────────────────────────────────────────────────────
if 'openFromHash();' not in s.split('function openFromHash')[-1][:4000]:
    m = re.search(r'\n\s*(renderDrivers\(\);|renderList\(\);)', s)
    if m:
        j = m.end()
        s = s[:j] + "\n  setTimeout(openFromHash,300);" + s[j:]
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
