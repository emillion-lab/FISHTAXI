import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# Голям QR на цял екран.
#
# Малкият код до аватара е труден за сканиране от задната седалка.
# Клик върху него отваря затъмнен слой с кода, преизчертан в голям
# размер — не увеличен (иначе се размазва и не се чете), а нарисуван
# наново от същия vCard.
#
# Ползва се готовият слой само ако е свободен; тук правим собствен,
# защото галерията работи с <img src>, а QR-ът е canvas.
# ─────────────────────────────────────────────────────────────────────

# 1. Слоят
OVERLAY = ('<div id="qr-big" onclick="closeQrBig()" style="display:none;'
           'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);'
           'align-items:center;justify-content:center;flex-direction:column;'
           'gap:16px;padding:20px;cursor:pointer">'
           '<div id="qr-big-box" style="background:#fff;padding:16px;'
           'border-radius:14px;line-height:0"></div>'
           '<div id="qr-big-name" style="color:#fff;font-size:16px;'
           'font-weight:700;text-align:center"></div>'
           '<div id="qr-big-sub" style="color:#9aa;font-size:13px;'
           'text-align:center"></div>'
           '<div style="color:#667;font-size:11px;margin-top:4px">'
           '\u0414\u043e\u043a\u043e\u0441\u043d\u0438 \u0437\u0430 \u0437\u0430\u0442\u0432\u0430\u0440\u044f\u043d\u0435</div>'
           '</div>')

if 'id="qr-big"' not in s:
    i = s.find('</body>')
    if i < 0:
        raise SystemExit("</body> not found")
    s = s[:i] + OVERLAY + '\n' + s[i:]
    report.append("fullscreen overlay added")
else:
    report.append("overlay: already there")

# 2. Функциите
HELPER = '''
/* Голям QR за сканиране от разстояние — например от задната седалка.
   Кодът се рисува наново в голям размер, а не се увеличава: увеличен
   canvas се размазва и четците се затрудняват.                    */
function openQrBig(){
  if(!cur)return;
  var lay=document.getElementById('qr-big');
  var box=document.getElementById('qr-big-box');
  if(!lay||!box)return;
  if(typeof QRCode==='undefined')return;
  box.innerHTML='';
  /* колкото permits екранът, но не по-голямо от 320 */
  var side=Math.max(200,Math.min(320,
    Math.floor(Math.min(window.innerWidth,window.innerHeight)*0.62)));
  try{
    new QRCode(box,{text:driverVCard(cur),width:side,height:side,
      colorDark:'#000000',colorLight:'#ffffff',
      correctLevel:QRCode.CorrectLevel.L});
  }catch(e){
    box.innerHTML='<span style="font-size:12px;color:#c00">QR: '
      +(e&&e.message?e.message:'error')+'</span>';
  }
  var nm=document.getElementById('qr-big-name');
  var sb=document.getElementById('qr-big-sub');
  if(nm)nm.textContent=dName(cur);
  if(sb)sb.textContent=(cur.phone||'')+(cur.car?'  \\u00b7  '+cur.car:'');
  lay.style.display='flex';
  /* докато е отворен, фонът не скролва */
  document.body.style.overflow='hidden';
}
function closeQrBig(){
  var lay=document.getElementById('qr-big');
  if(lay)lay.style.display='none';
  document.body.style.overflow='';
}
'''

if 'function openQrBig' not in s:
    anchor = 'function renderDriverQR('
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("renderDriverQR anchor not found")
    s = s[:i] + HELPER.lstrip('\n') + '\n' + s[i:]
    report.append("openQrBig / closeQrBig added")
else:
    report.append("functions: already there")

# 3. Малкият QR става кликаем
OLD_BOX = ('<div id="m-qr" style="background:#fff;padding:5px;'
           'border-radius:8px;line-height:0"></div>')
NEW_BOX = ('<div id="m-qr" onclick="openQrBig()" title="'
           '\u0414\u043e\u043a\u043e\u0441\u043d\u0438 \u0437\u0430 \u0433\u043e\u043b\u044f\u043c QR" '
           'style="background:#fff;padding:5px;border-radius:8px;'
           'line-height:0;cursor:pointer"></div>')
if OLD_BOX in s:
    s = s.replace(OLD_BOX, NEW_BOX, 1)
    report.append("small QR is now clickable")
elif 'onclick="openQrBig()"' in s:
    report.append("click handler: already there")
else:
    report.append("QR box anchor not matched - SKIPPED")

# 4. Esc затваря слоя
if "closeQrBig();" not in s.split('addEventListener(\'keydown\'')[-1][:400]:
    m = re.search(r"document\.getElementById\('modal'\)\.addEventListener", s)
    if m:
        ins = m.start()
        s = (s[:ins] +
             "document.addEventListener('keydown',function(e){"
             "if(e.key==='Escape')closeQrBig();});\n" + s[ins:])
        report.append("Esc closes overlay")
    else:
        report.append("Esc hook: anchor not found - SKIPPED")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
