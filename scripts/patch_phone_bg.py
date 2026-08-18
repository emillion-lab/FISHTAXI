#!/usr/bin/env python3
# FT-PHONE-NAT
# Клиентката с iPhone видяла "+359878592888" и решила, че липсва нулата.
# Номерът е верен — 0878592888 и +359878592888 са едно и също. Затова:
#   1) показваме националния запис (0878 592 888) до бутоните за обаждане,
#      а линкът остава международен, за да работи и от чужбина;
#   2) Viber deep link-овете получават %2B — без плюса iOS Viber често
#      не намира контакта и поръчката увисва.
import io, sys

FILES = ['index.html', 'next/index.html']
MARK = 'FT-PHONE-NAT'

HELPERS = """/* FT-PHONE-NAT — националният запис е това, което българският клиент
   разпознава. Линкът остава +359…, за да звъни и от чужбина. */
function natPhone(p){
  var d=String(p||'').replace(/[^0-9]/g,'');
  if(d.indexOf('359')===0){return ('0'+d.slice(3)).replace(/^(\\d{4})(\\d{3})(\\d{3})$/,'$1 $2 $3');}
  return '+'+d;
}
function setDriverPhone(d){
  var host=document.getElementById('mcar2');
  if(!host||!d||!d.phone)return;
  var el=document.getElementById('mphone');
  if(!el){
    el=document.createElement('div');el.id='mphone';
    el.style.cssText='margin-top:6px;font-size:14px;font-weight:600;letter-spacing:.3px';
    host.parentNode.insertBefore(el,host.nextSibling);
  }
  var intl=String(d.phone).replace(/[^0-9+]/g,'');
  el.innerHTML='<a href="tel:'+intl+'" style="color:var(--y,#e8b923);text-decoration:none">&#9742; '+natPhone(d.phone)+'</a>';
}
"""

ANCHOR = "function doCall(){"

CARD_ANCHORS = [
    "document.getElementById('mcar2').textContent=d.car+' · '+d.plate;",
    "document.getElementById('mcar2').innerHTML=_e(d.car)+'<span class=\"plate\"><i>BG</i>'+_e(d.plate)+'</span>';",
]

changed = []
for path in FILES:
    try:
        s = io.open(path, encoding='utf-8').read()
    except IOError:
        print('SKIP (липсва): ' + path)
        continue

    if MARK in s:
        print('SKIP (вече е приложено): ' + path)
        continue

    # 1. Viber deep link без плюс → iOS не резолвва контакта
    n_viber = s.count('viber://chat?number=')
    if n_viber == 0:
        print('FAIL: няма viber chat линкове в ' + path)
        sys.exit(1)
    s = s.replace('viber://chat?number=', 'viber://chat?number=%2B')

    # 2. Помощните функции
    if ANCHOR not in s:
        print('FAIL: липсва котвата doCall в ' + path)
        sys.exit(1)
    s = s.replace(ANCHOR, HELPERS + ANCHOR, 1)

    # 3. Извикване при рендер на картончето
    hit = None
    for a in CARD_ANCHORS:
        if a in s:
            hit = a
            break
    if hit is None:
        print('FAIL: липсва котвата mcar2 в ' + path)
        sys.exit(1)
    s = s.replace(hit, hit + '\n  setDriverPhone(d);', 1)

    io.open(path, 'w', encoding='utf-8').write(s)
    changed.append(path + ' (viber x' + str(n_viber) + ')')

print('OK: ' + (', '.join(changed) if changed else 'нищо за промяна'))
