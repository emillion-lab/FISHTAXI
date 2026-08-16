# -*- coding: utf-8 -*-
# fish.taxi · визуален патч v1
#
# Тезата: fish.taxi показва истински човек и истинска кола, а конкурентите
# показват анонимен диспечер. Значи колата и човекът трябва да са героят,
# а не жълтото.
#
# Три хода:
#   1. ДВА ГЛАСА В ТИПОГРАФИЯТА. Машинният глас (номера, цени, филтри,
#      табове) минава на тесен signage шрифт — езикът на табелите и
#      таксиметровия апарат. Човешкият глас (имена, био) остава системен
#      и топъл. Разликата се вижда, без да се обяснява.
#   2. ПОДПИСЪТ: регистрационният номер се рисува като истинска табела,
#      със синята лента и BG. Никое такси приложение не показва това,
#      защото всички крият колата. Ние я показваме.
#   3. ТИШИНА. Имаше шест безкрайни анимации едновременно. Остава една —
#      подредено появяване на картите при зареждане. Останалото е шум,
#      който яде батерия и разсейва човек на улицата.
#
# Употреба:  python3 patch_design.py next/index.html
# Идемпотентен: втори пуск не прави нищо.
import io, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = io.open(p, encoding='utf-8').read()
n0 = len(s)

if 'FT-DESIGN-V1' in s:
    print('SKIP: design patch already applied'); sys.exit(0)

def rep(old, new, tag, expect=1):
    global s
    if s.count(old) != expect:
        print('FAIL anchor (%d hits, expected %d): %s' % (s.count(old), expect, tag))
        sys.exit(1)
    s = s.replace(old, new)
    print(' -', tag)

# ── 1. Шрифт за машинния глас ────────────────────────────────────────
# Oswald: тесен, с кирилица, четим при малък кегел. display=swap значи,
# че страницата не чака шрифта — офлайн просто пада към системния.
rep(
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>',
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&display=swap">\n'
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>',
    'Oswald зареден (swap, с fallback)'
)

# ── 2. Табелата в картата на шофьора ────────────────────────────────
rep(
    """html+='<div class="dcc">'+d.car+' &middot; '+d.plate+'</div>';""",
    """html+='<div class="dcc">'+d.car+'<span class="plate"><i>BG</i>'+d.plate+'</span></div>';""",
    'табела в картата'
)
rep(
    """document.getElementById('mcar2').textContent=d.car+' · '+d.plate;""",
    """var _e=function(v){return String(v==null?'':v).replace(/[<>&"]/g,function(c){return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c];});};
  document.getElementById('mcar2').innerHTML=_e(d.car)+'<span class="plate"><i>BG</i>'+_e(d.plate)+'</span>';""",
    'табела в профила'
)

# ── 3. Целият нов слой стил ─────────────────────────────────────────
CSS = u"""
/* ══════════════ FT-DESIGN-V1 ══════════════
   Два гласа: машинен (Oswald, тесен) и човешки (системен, топъл).
   Всичко под този коментар има предимство пред горното. */

:root{
  --machine:"Oswald","Roboto Condensed","Segoe UI Variable Display",system-ui,sans-serif;
  --plateBlue:#003399;
  --live:#12b76a;
}

/* ── машинният глас: числа, статуси, навигация ── */
.tab,.fl,.flt,.rb,.mh,.pi2,.iv,.vb,.founder{font-family:var(--machine);letter-spacing:.02em}
.tab{font-weight:500;text-transform:uppercase;letter-spacing:.06em}
.fl{font-weight:500;letter-spacing:.1em}
.flt{font-weight:400}
.flt.on{font-weight:600}
.rb,.iv{font-variant-numeric:tabular-nums;font-weight:500}
.mh{font-weight:500;letter-spacing:.14em}

/* ── човешкият глас: имената дишат ── */
.dcn{font-family:inherit;font-weight:800;font-size:17px;letter-spacing:-.01em;line-height:1.25}
.mn{font-family:inherit;font-weight:800;font-size:22px;letter-spacing:-.02em}
.dcc{font-family:var(--machine);font-weight:400;display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:2px}

/* ── ПОДПИСЪТ: регистрационният номер като истинска табела ── */
.plate{
  display:inline-flex;align-items:stretch;height:19px;border-radius:3px;overflow:hidden;
  border:1px solid #23262d;background:#f2f2ef;color:#14161a;
  font-family:var(--machine);font-weight:600;font-size:12px;letter-spacing:.09em;
  font-variant-numeric:tabular-nums;line-height:17px;flex-shrink:0;
  box-shadow:0 1px 0 rgba(0,0,0,.28);padding-right:7px;
}
.plate i{
  display:flex;align-items:center;justify-content:center;font-style:normal;
  background:var(--plateBlue);color:#fff;font-size:8px;font-weight:500;
  letter-spacing:.04em;padding:0 3px;margin-right:6px;min-width:15px;
}
#mcar2 .plate{height:23px;font-size:14px;line-height:21px;vertical-align:-4px;margin-left:8px}

/* ── по-малко цветове: запазваме нюанса, махаме заливките ── */
.t{background:transparent!important;font-weight:600;padding:3px 8px;border-radius:7px}
.tg,.ty,.tb,.tc,.tr,.tp,.to,.tpi{background:transparent!important}
.tb,.tc,.tp,.to,.tpi{color:var(--mu)!important;border-color:var(--brd)!important}
.pi2{background:transparent;font-weight:500}

/* „на линия" е единственото, което свети — статусът е новината */
.vb{color:var(--live);border-color:rgba(18,183,106,.45);background:rgba(18,183,106,.08)}

/* ── картата на шофьора: спокойна, с една ясна ос ── */
.dc{border-radius:16px;padding:13px}
.dca{width:60px;height:60px;border-radius:14px}
.dcb{margin-top:11px}

/* ── ЕДИНСТВЕНАТА анимация: картите се подреждат при зареждане ── */
@keyframes ftIn{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
.dlist .dc,#map-list .dc{animation:ftIn .42s cubic-bezier(.22,1,.36,1) both}
.dlist .dc:nth-child(1),#map-list .dc:nth-child(1){animation-delay:.02s}
.dlist .dc:nth-child(2),#map-list .dc:nth-child(2){animation-delay:.07s}
.dlist .dc:nth-child(3),#map-list .dc:nth-child(3){animation-delay:.12s}
.dlist .dc:nth-child(4),#map-list .dc:nth-child(4){animation-delay:.17s}
.dlist .dc:nth-child(n+5),#map-list .dc:nth-child(n+5){animation-delay:.21s}

/* ── ТИШИНА: шестте безкрайни анимации отпадат ── */
[data-theme="dark"] .top{animation:none}
#simple-hero button[onclick^="orderNowSimple"]::after{display:none}
.fs:first-of-type .flt:nth-of-type(1),
.fs:first-of-type .flt:nth-of-type(2){animation:none}
.spark{display:none}
.hint-tabs{animation:none}
.hint-photo::after{animation:none}
.founder{animation:none;background:linear-gradient(100deg,#e8b91a,#f7d874);font-family:var(--machine);font-weight:500}
.dc.ft-spotlight{transform:none;box-shadow:none}
.dc.ft-dim{opacity:1}

/* ── героят: по-малко крясък, повече обещание ── */
#simple-hero{padding:12px}
#simple-hero>button{font-family:var(--machine)!important;font-weight:600!important;
  letter-spacing:.04em!important;border-radius:14px!important}

@media (prefers-reduced-motion:reduce){
  .dlist .dc,#map-list .dc{animation:none}
}
"""

rep('\n</style>\n', CSS + '\n</style>\n', 'новият стилов слой')

io.open(p, 'w', encoding='utf-8').write(s)
print('OK  %d -> %d chars' % (n0, len(s)))
