#!/usr/bin/env python3
"""FT-LROLL-V2 (17.11.2026): ролката за езика е плаващ бутон под менюто.

Маха групата „Език“ от менюто и блока FT-LROLL-V1 от lib/app-ui.js; слага плаваща ролка
(#lroll) със знамена; texts() я прерисува при смяна на езика. Стилът е в lib/app-lang.css.
Идемпотентен; всяка котва трябва да е точно веднъж."""
import io, sys

def rd(p):
    return io.open(p, encoding='utf-8').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)

def one(s, old, new, what):
    n = s.count(old)
    if n != 1:
        print('котвата "%s" не е точно веднъж: %d' % (what, n)); sys.exit(1)
    return s.replace(old, new)

P = 'lib/app-ui.js'
s = rd(P)
if 'FT-LROLL-V2' in s:
    print(P, ': вече е приложен — SKIP')
else:
    # 1) групата „Език“ излиза от менюто
    s = one(s, "'<div class=\"pgrp\"><h3>'+t('lang')+'</h3>'+langRoll()+'</div>'+", "''+", 'меню')

    # 2) старият блок V1 (ролка в менюто) се заменя
    start = s.find('/* FT-LROLL-V1:')
    tail = "F.buzz(8);F.setLang(b.dataset.l);texts();renderMenu();\n});"
    end = s.find(tail)
    if start < 0 or end < 0 or s.count('/* FT-LROLL-V1:') != 1 or s.count(tail) != 1:
        print('блокът V1 не е намерен точно веднъж'); sys.exit(1)
    end += len(tail)
    new_block = r'''/* FT-LROLL-V2: ролка за езика под менюто — активният е най-отгоре, докосване разгъва останалите */
var lroll=document.createElement('div');lroll.id='lroll';document.body.appendChild(lroll);
function renderRoll(){
  var o=[F.lang].concat(F.LANGS.filter(function(l){return l!==F.lang;}));
  function fl(l){return F.FLAG[l]||'🏳️';}
  lroll.className='';
  lroll.innerHTML='<button class="round glassy lcur" id="lcur" aria-expanded="false" aria-label="'+esc(t('lang')+': '+F.LN[o[0]])+'"><span>'+fl(o[0])+'</span></button>'+
   '<div class="lrest"><div class="lin">'+o.slice(1).map(function(l,i){return '<button class="round glassy lopt" data-l="'+l+'" style="--i:'+i+'" aria-label="'+esc(F.LN[l])+'"><span>'+fl(l)+'</span></button>';}).join('')+'</div></div>';
}
function rollOpen(on){lroll.classList.toggle('open',on);var c=$('lcur');if(c)c.setAttribute('aria-expanded',on);}
lroll.addEventListener('click',function(e){
  if(e.target.closest('#lcur')){rollOpen(!lroll.classList.contains('open'));F.buzz(8);return;}
  var b=e.target.closest('[data-l]');if(!b)return;
  F.buzz(8);F.setLang(b.dataset.l);texts();
});
document.addEventListener('click',function(e){if(lroll.classList.contains('open')&&!e.target.closest('#lroll'))rollOpen(false);});'''
    s = s[:start] + new_block + s[end:]

    # 3) прерисуване при смяна на езика
    s = one(s, "renderChips();lastSig='';renderList();hud();measure();",
            "renderChips();lastSig='';renderList();hud();measure();renderRoll();", 'texts')
    wr(P, s); print(P, ': ролка v2 (плаваща)')

for P in ('index.html', 'app.html'):
    s = rd(P)
    if 'lib/app-ui.js?v=13' in s:
        print(P, ': вече е вдигнат — SKIP'); continue
    s = one(s, 'lib/app-ui.js?v=12', 'lib/app-ui.js?v=13', P + ' ui')
    s = one(s, 'lib/app-lang.css?v=1', 'lib/app-lang.css?v=2', P + ' css')
    wr(P, s); print(P, ': ?v= вдигнат')
print('FT-LROLL-V2 готово')
