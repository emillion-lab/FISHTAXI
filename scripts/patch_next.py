import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if b in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

def app(p, marker, block):
    s = io.open(p, encoding='utf-8').read()
    if marker in s:
        print('already:', p, marker); return
    io.open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + marker + '\n' + block + '\n')
    print('ok:', p, marker)

# QR визитка в профила на шофьора + цял екран при докосване
sub('lib/app-ui.js', "function openProf(d){", r"""function vcard(d){
  var nm=String(d.name||'Driver').replace(/[^\x20-\x7E]/g,'').trim()||'Driver';
  var L=['BEGIN:VCARD','VERSION:3.0','N:;'+nm+';;;','FN:'+nm,'ORG:fish.taxi','TEL;TYPE=CELL:'+F.tel(d),'URL:'+location.origin+location.pathname+'#d'+d.id];
  var car=String(d.car||'').replace(/[^\x20-\x7E]/g,'').trim();
  if(car&&(L.join('\n').length+car.length+12)<230)L.push('NOTE:'+car);
  L.push('END:VCARD');return L.join('\n');
}
function qrDraw(box,d,side){box.innerHTML='';if(typeof QRCode==='undefined')return;try{new QRCode(box,{text:vcard(d),width:side,height:side,colorDark:'#000000',colorLight:'#ffffff',correctLevel:QRCode.CorrectLevel.L});}catch(e){}}
function qrGroup(d){var bg=F.lang==='bg';return '<div class="pgrp pqr"><button class="qrb" data-qr="'+d.id+'"><span class="qrbox" id="pqr"></span><span class="qrt">'+(bg?'QR за контактите.<br>Докосни за цял екран':'Contact QR.<br>Tap for full screen')+'</span></button></div>';}
function bigQr(d){var o=document.createElement('div');o.id='qrbig';var side=Math.max(200,Math.min(320,Math.floor(Math.min(innerWidth,innerHeight)*.62)));o.innerHTML='<div class="qrbox"></div><b>'+esc(F.name(d))+'</b><span class="s">'+esc(F.natPhone(d.phone))+'</span><span class="s">'+(F.lang==='bg'?'Докосни за затваряне':'Tap to close')+'</span>';document.body.appendChild(o);qrDraw(o.firstChild,d,side);o.onclick=function(){o.remove();};}
$('pbody').addEventListener('click',function(e){var b=e.target.closest('[data-qr]');if(!b)return;var d=F.byId(b.dataset.qr);if(d)bigQr(d);});
function openProf(d){""")
sub('lib/app-ui.js', "F.natPhone(d.phone)+'</a>')+'</div>';\n  $('pbody').scrollTop=0;",
 "F.natPhone(d.phone)+'</a>')+'</div>'+qrGroup(d);\n  $('pbody').scrollTop=0;qrDraw($('pqr'),d,96);")

app('lib/app.css', '/* v3.7 qr */',
""".pqr{padding:12px}
.qrb{display:flex;align-items:center;gap:14px;width:100%;text-align:left}
.qrbox{background:#fff;padding:6px;border-radius:10px;line-height:0;flex:none}
.qrt{font-size:15px;color:var(--dust);line-height:1.35}
#qrbig{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.92);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;padding:20px;cursor:pointer}
#qrbig .qrbox{padding:16px;border-radius:14px}
#qrbig b{color:#fff;font-size:22px}
#qrbig .s{color:#9aa;font-size:15px}""")

s = io.open('index.html', encoding='utf-8').read()
if 'lib/qrcode.min.js' not in s:
    s = s.replace('<script src="lib/app-ui.js?v=9"></script>', '<script src="lib/qrcode.min.js"></script>\n<script src="lib/app-ui.js?v=10"></script>')
for old, new in [('app.css?v=3', 'app.css?v=4')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)
