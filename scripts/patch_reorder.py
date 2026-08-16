# -*- coding: utf-8 -*-
# fish.taxi · пренареждане на панела на шофьора (v3)
#
# Проблемът: поръчката стоеше на дъното на дълъг скрол — цена, детайли,
# снимки, плащане, езици, четиринайсет опции, райони, био — и чак после
# бутоните. Човек се уморява, преди да стигне до действието.
#
# Новият ред:
#   човекът (снимка, име, табела, рейтинг)
#   стилът на каране
#   цената          <- краткото, което решава
#   снимките        <- доверието
#   ПОРЪЧКА         <- действието идва тук
#   бутоните
#   „Още за шофьора и колата"  <- сгънато, отваря се при нужда
#
# Прави се от DOM, не с пренаписване на HTML: по-безопасно е и
# оцелява при бъдещи промени по разметката.
#
# Употреба: python3 scripts/patch_reorder.py next/index.html
# Пуска се СЛЕД patch_design.py. Идемпотентен.
import io, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = io.open(p, encoding='utf-8').read()
n0 = len(s)

if 'FT-REORDER-V3' in s:
    print('SKIP: reorder already applied'); sys.exit(0)

JS = u"""
<script>
/* FT-REORDER-V3 — поръчката се вдига нагоре, справочното се сгъва */
(function(){
  function reorder(){
    var mb = document.querySelector('.mb');
    if(!mb || mb.dataset.ftReordered) return;

    var order  = document.getElementById('mh-order');
    var btns   = mb.querySelector('.mbtns');
    var photos = document.getElementById('mphotos');
    if(!order || !btns || !photos) return;

    /* 1. блокът на поръчката: от „Преди да поръчаш" до бутоните включително */
    var block = [], n = order;
    while(n && n !== btns){ block.push(n); n = n.nextElementSibling; }
    block.push(btns);

    /* 2. справочните секции — поименно, за да не глътнат нещо чуждо */
    var foldIds = ['mh-cardet','mcardet','mh-pay','mpay','mh-langs','mlangs',
                   'mh-opts','mopts','mh-areas','mareas','mh-about','mbio'];
    var foldNodes = foldIds.map(function(id){ return document.getElementById(id); })
                           .filter(Boolean);

    /* 3. поръчката се вдига веднага след снимките */
    var anchor = photos;
    block.forEach(function(el){
      anchor.parentNode.insertBefore(el, anchor.nextSibling);
      anchor = el;
    });

    /* 4. справочното отива под бутоните, сгънато в едно */
    if(foldNodes.length){
      var det = document.createElement('details');
      det.className = 'ft-fold';
      var sum = document.createElement('summary');
      sum.id = 'ft-fold-sum';
      sum.textContent = (document.documentElement.lang === 'bg')
        ? 'Още за шофьора и колата'
        : 'More about the driver and car';
      det.appendChild(sum);
      btns.parentNode.insertBefore(det, btns.nextSibling);
      foldNodes.forEach(function(el){ det.appendChild(el); });
    }

    mb.dataset.ftReordered = '1';
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', reorder);
  } else {
    reorder();
  }

  /* езикът се сменя динамично — обновяваме надписа на сгъването */
  var oldSetLang = window.setLang;
  if(typeof oldSetLang === 'function'){
    window.setLang = function(v){
      var r = oldSetLang.apply(this, arguments);
      var sum = document.getElementById('ft-fold-sum');
      if(sum) sum.textContent = (v === 'bg')
        ? 'Още за шофьора и колата'
        : 'More about the driver and car';
      return r;
    };
  }
})();
</script>
"""

CSS = u"""
/* ═══ FT-REORDER-V3: сгъваемото справочно ═══ */
.ft-fold{margin:18px 0 8px;border-radius:var(--m3-md,16px);
  background:var(--m3-sc,#f7ecdc);overflow:hidden}
.ft-fold>summary{list-style:none;cursor:pointer;padding:16px 18px;
  font-size:15px;font-weight:600;color:var(--m3-on-surface,#1f1b13);
  display:flex;align-items:center;justify-content:space-between;
  -webkit-tap-highlight-color:transparent}
.ft-fold>summary::-webkit-details-marker{display:none}
.ft-fold>summary::after{content:'⌄';font-size:19px;line-height:1;
  color:var(--m3-on-surface-var,#4e4639);
  transition:transform 220ms cubic-bezier(.2,0,0,1)}
.ft-fold[open]>summary::after{transform:rotate(180deg)}
.ft-fold[open]>summary{border-bottom:1px solid var(--m3-outline-var,#d1c5b4)}
.ft-fold>*:not(summary){margin-left:18px;margin-right:18px}
.ft-fold>*:last-child{margin-bottom:16px}
.ft-fold .mh:first-of-type{margin-top:14px}

/* цената е кратка и решаваща — остава видима и се откроява */
#mprice{font-size:17px!important;font-weight:700!important;
  color:var(--m3-on-surface,#1f1b13)!important;
  background:var(--m3-primary-c,#ffdf95);border-radius:var(--m3-sm,12px);
  padding:12px 14px;line-height:1.45}

/* поръчката вече е високо — заглавието ѝ носи повече тежест */
#mh-order{font-size:13px!important;letter-spacing:.09em!important;margin-top:22px!important}
"""

s = s.replace('\n</style>\n', CSS + '\n</style>\n', 1)
s = s.replace('</body>', JS + '</body>', 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('OK  %d -> %d chars' % (n0, len(s)))
