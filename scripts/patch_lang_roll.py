#!/usr/bin/env python3
"""FT-LROLL-V1 (17.11.2026): изборът на език в менюто е „ролка“ със знамена.

Затворена — само активният език най-отгоре; докосване го разгъва и показва
останалите. Избор → езикът се сменя и ролката се затваря.
Пипа lib/app-ui.js (renderMenu + обработчика в менюто) и вързва lib/app-lang.css
в index.html и app.html. Идемпотентен; всяка котва трябва да е точно веднъж."""
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

# 1) lib/app-ui.js
P = 'lib/app-ui.js'
s = rd(P)
if 'FT-LROLL-V1' in s:
    print(P, ': вече е приложен — SKIP')
else:
    old_menu = ('<div class="seg">\'+F.LANGS.map(function(l){return \'<button class="chip" data-l="\'+l+\'" '
                'aria-pressed="\'+(F.lang===l)+\'">\'+F.LN[l]+\'</button>\';}).join(\'\')+\'</div></div>\'+')
    new_menu = '\'+langRoll()+\'</div>\'+'
    s = one(s, old_menu, new_menu, 'renderMenu')

    old_click = ("$('mbody').addEventListener('click',function(e){var b=e.target.closest('[data-l]');"
                 "if(!b)return;F.setLang(b.dataset.l);texts();renderMenu();});")
    new_click = r'''/* FT-LROLL-V1: ролка за езика — активният най-отгоре, докосване разгъва останалите */
function langRoll(){
  var o=[F.lang].concat(F.LANGS.filter(function(l){return l!==F.lang;}));
  function fl(l){return F.FLAG[l]||'🏳️';}
  return '<div class="roll" id="roll"><button class="rl cur" data-roll="1" aria-expanded="false"><span class="fl">'+fl(o[0])+'</span><b>'+F.LN[o[0]]+'</b><i class="chev"></i></button>'+
   '<div class="rest"><div class="rin">'+o.slice(1).map(function(l,i){return '<button class="rl" data-l="'+l+'" style="--i:'+i+'"><span class="fl">'+fl(l)+'</span><b>'+F.LN[l]+'</b></button>';}).join('')+'</div></div></div>';
}
$('mbody').addEventListener('click',function(e){
  var r=e.target.closest('[data-roll]');
  if(r){var box=$('roll'),on=!box.classList.contains('open');box.classList.toggle('open',on);r.setAttribute('aria-expanded',on);F.buzz(8);return;}
  var b=e.target.closest('[data-l]');if(!b)return;
  F.buzz(8);F.setLang(b.dataset.l);texts();renderMenu();
});'''
    s = one(s, old_click, new_click, 'click')
    wr(P, s); print(P, ': ролка добавена')

# 2) CSS + cache-bust в страниците
for P, anchor in (('index.html', '<link rel="stylesheet" href="lib/app-day.css?v=4">'),
                  ('app.html', '<link rel="stylesheet" href="lib/app.css?v=1">')):
    s = rd(P)
    if 'lib/app-lang.css' in s:
        print(P, ': вече е вързан — SKIP'); continue
    s = one(s, anchor, anchor + '\n<link rel="stylesheet" href="lib/app-lang.css?v=1">', P + ' css')
    s = one(s, 'lib/app-ui.js?v=11', 'lib/app-ui.js?v=12', P + ' ui')
    wr(P, s); print(P, ': app-lang.css вързан, app-ui.js ?v=12')
print('FT-LROLL-V1 готово')
