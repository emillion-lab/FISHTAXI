# -*- coding: utf-8 -*-
# fish.taxi · Material 3 основа (v2)
#
# Не е шлифовка на стария дизайн — това е смяна на системата отдолу.
#
# Какво влиза:
#   ТОКЕНИ      цветови роли по M3 (primary / surface tiers / outline),
#               изведени от таксиметровото жълто като seed
#   ФОРМА       shape scale: 8 / 12 / 16 / 20 / 28 / full
#   ВИСОЧИНА    тонална — нивата се различават по повърхност, не по сянка
#   ТИПОГРАФИЯ  M3 ramp, върху системния шрифт (без външна зависимост)
#   СЪСТОЯНИЯ   state layers при натискане
#   КОМПОНЕНТИ  bottom sheet с дръжка, segmented button, filter chips,
#               outlined text fields, filled/tonal buttons, primary tabs,
#               filled cards, top app bar
#
# Употреба:  python3 scripts/patch_design.py next/index.html
# Идемпотентен.
import io, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = io.open(p, encoding='utf-8').read()
n0 = len(s)

if 'FT-M3-V2' in s:
    print('SKIP: M3 patch already applied'); sys.exit(0)

def rep(old, new, tag, expect=1):
    global s
    if s.count(old) != expect:
        print('FAIL anchor (%d hits, expected %d): %s' % (s.count(old), expect, tag))
        sys.exit(1)
    s = s.replace(old, new)
    print(' -', tag)

# ── Табелата: регистрационният номер като истинска табела ───────────
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

# ── Дръжка на bottom sheet ─────────────────────────────────────────
rep(
    '<div class="mb">',
    '<div class="mb"><div class="m3-handle" aria-hidden="true"></div>',
    'дръжка на панела', expect=s.count('<div class="mb">')
)

CSS = u"""
/* ═══════════════════ FT-M3-V2 ═══════════════════
   Material 3 основа. Всичко под този коментар определя системата;
   старите правила остават само там, където M3 не ги покрива.
   Много елементи имат inline стилове, затова тук се използва
   !important — нарочно, не по небрежност. */

:root{
  /* ─ форма ─ */
  --m3-xs:8px; --m3-sm:12px; --m3-md:16px; --m3-lg:20px; --m3-xl:28px; --m3-full:999px;
  /* ─ движение ─ */
  --m3-emph:cubic-bezier(.2,0,0,1);
  --m3-std:cubic-bezier(.2,0,0,1);
  --m3-short:180ms; --m3-med:300ms; --m3-long:450ms;
}

/* ─ цветови роли: светла схема ─ */
:root{
  --m3-primary:#785900;        --m3-on-primary:#ffffff;
  --m3-primary-c:#ffdf95;      --m3-on-primary-c:#251a00;
  --m3-secondary-c:#ede1c2;    --m3-on-secondary-c:#231b04;
  --m3-surface:#fff8ef;        --m3-on-surface:#1f1b13;
  --m3-surface-dim:#e2d9cc;
  --m3-sc-lowest:#ffffff;      --m3-sc-low:#fdf1e2;
  --m3-sc:#f7ecdc;             --m3-sc-high:#f1e6d7;
  --m3-sc-highest:#ebe0d1;
  --m3-on-surface-var:#4e4639; --m3-outline:#807667;
  --m3-outline-var:#d1c5b4;
  --m3-success:#1c6c46;        --m3-on-success-c:#00210f;
  --m3-success-c:#a4f2c4;
  --m3-error:#ba1a1a;          --m3-error-c:#ffdad6;
  --m3-scrim:rgba(0,0,0,.42);
  --m3-state:#1f1b13;
}
/* ─ цветови роли: тъмна схема ─ */
[data-theme="dark"]{
  --m3-primary:#f0c33f;        --m3-on-primary:#3f2e00;
  --m3-primary-c:#5b4300;      --m3-on-primary-c:#ffdf95;
  --m3-secondary-c:#4e4739;    --m3-on-secondary-c:#ede1c2;
  --m3-surface:#16130b;        --m3-on-surface:#eae1d3;
  --m3-surface-dim:#16130b;
  --m3-sc-lowest:#100e07;      --m3-sc-low:#1f1b13;
  --m3-sc:#231f17;             --m3-sc-high:#2e2921;
  --m3-sc-highest:#39342b;
  --m3-on-surface-var:#d1c5b4; --m3-outline:#9a8f80;
  --m3-outline-var:#4e4639;
  --m3-success:#88d6a9;        --m3-on-success-c:#a4f2c4;
  --m3-success-c:#00522f;
  --m3-error:#ffb4ab;          --m3-error-c:#93000a;
  --m3-scrim:rgba(0,0,0,.62);
  --m3-state:#eae1d3;
}

/* ─ старите променливи се пренасочват към M3 ролите,
     за да поеме системата и това, което не е пипано поименно ─ */
:root,[data-theme="dark"]{
  --bg:var(--m3-surface); --s1:var(--m3-sc-low); --s2:var(--m3-sc);
  --s3:var(--m3-sc-high); --brd:var(--m3-outline-var);
  --tx:var(--m3-on-surface); --mu:var(--m3-on-surface-var);
  --mu2:var(--m3-outline); --y:var(--m3-primary);
}

/* ─ типографска стълба ─ */
body{font-size:14px;line-height:1.43;letter-spacing:.0125em}

/* ═══ ПОВЪРХНОСТИ ═══ */
html,body{background:var(--m3-surface)}
.top{background:var(--m3-sc)!important;border-bottom:none!important;height:60px;
  box-shadow:none;animation:none!important}
.tabs{background:var(--m3-surface);border-bottom:1px solid var(--m3-outline-var)}

/* ═══ TABS: M3 primary tabs ═══ */
.tab{position:relative;background:transparent;color:var(--m3-on-surface-var);
  font-size:13px;font-weight:600;letter-spacing:.01em;padding:13px 4px 12px;
  border-bottom:none;overflow:hidden;transition:color var(--m3-short) var(--m3-std)}
.tab::before{content:'';position:absolute;inset:0;background:var(--m3-state);
  opacity:0;transition:opacity var(--m3-short) var(--m3-std)}
.tab:active::before{opacity:.1}
.tab.on{color:var(--m3-primary)}
.tab.on::after{content:'';position:absolute;left:50%;transform:translateX(-50%);
  bottom:0;width:56%;height:3px;border-radius:3px 3px 0 0;background:var(--m3-primary);
  animation:m3Ind var(--m3-med) var(--m3-emph)}
@keyframes m3Ind{from{width:0}to{width:56%}}

/* ═══ CARDS: M3 filled card ═══ */
.dc{background:var(--m3-sc)!important;border:none!important;border-radius:var(--m3-lg);
  padding:14px;margin-bottom:10px;position:relative;overflow:hidden;
  box-shadow:none!important;backdrop-filter:none!important;
  transition:background var(--m3-short) var(--m3-std)}
.dc::before{content:'';position:absolute;inset:0;background:var(--m3-state);
  opacity:0;transition:opacity var(--m3-short) var(--m3-std);pointer-events:none}
.dc:active::before{opacity:.1}
.dc.ft-spotlight{transform:none;box-shadow:none}
.dc.ft-dim{opacity:1}
.dca{width:60px;height:60px;border-radius:var(--m3-md);background:var(--m3-sc-highest);
  border:none}
.dcn{font-size:17px;font-weight:600;letter-spacing:-.005em;line-height:1.3;
  color:var(--m3-on-surface)}
.dcc{font-size:13px;color:var(--m3-on-surface-var);display:flex;align-items:center;
  gap:8px;flex-wrap:wrap;margin-top:3px}
.rb{font-size:14px;font-weight:600;color:var(--m3-on-surface-var);
  font-variant-numeric:tabular-nums}

/* ═══ ПОДПИСЪТ: регистрационният номер като табела ═══ */
.plate{display:inline-flex;align-items:stretch;height:20px;border-radius:4px;
  overflow:hidden;background:#f4f2ec;color:#16181c;
  font:600 12px/18px ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  letter-spacing:.06em;flex-shrink:0;padding-right:7px;
  box-shadow:0 0 0 1px rgba(0,0,0,.35)}
.plate i{display:flex;align-items:center;justify-content:center;font-style:normal;
  background:#003399;color:#fff;font-size:8px;font-weight:700;letter-spacing:.02em;
  padding:0 3px;margin-right:6px;min-width:15px}
#mcar2 .plate{height:24px;font-size:14px;line-height:22px;margin-left:8px}

/* ═══ CHIPS: M3 filter chip ═══ */
.flt,.pref-btn{height:36px;padding:0 16px!important;border-radius:var(--m3-xs)!important;
  border:1px solid var(--m3-outline)!important;background:transparent!important;
  color:var(--m3-on-surface-var)!important;font-size:14px!important;font-weight:600!important;
  letter-spacing:.007em;position:relative;overflow:hidden;
  transition:background var(--m3-short) var(--m3-std),border-color var(--m3-short) var(--m3-std);
  animation:none!important;box-shadow:none!important}
.flt::before,.pref-btn::before{content:'';position:absolute;inset:0;
  background:var(--m3-state);opacity:0;transition:opacity var(--m3-short) var(--m3-std)}
.flt:active::before,.pref-btn:active::before{opacity:.1}
.flt.on,.pref-btn.on{background:var(--m3-secondary-c)!important;
  border-color:transparent!important;color:var(--m3-on-secondary-c)!important}
.fl{font-size:11px;font-weight:600;letter-spacing:.09em;color:var(--m3-on-surface-var)}

/* ═══ SEGMENTED BUTTON: Сега / Резервирай ═══ */
#lbl-when + div{gap:0!important}
#btn-when-now,#btn-when-later{height:40px;border-radius:0!important;margin:0!important;
  border:1px solid var(--m3-outline)!important}
#btn-when-now{border-radius:var(--m3-full) 0 0 var(--m3-full)!important;
  border-right-width:0!important}
#btn-when-later{border-radius:0 var(--m3-full) var(--m3-full) 0!important}
#btn-when-now.on,#btn-when-later.on{background:var(--m3-secondary-c)!important;
  border-color:var(--m3-outline)!important;color:var(--m3-on-secondary-c)!important}

/* ═══ TEXT FIELDS: M3 outlined ═══ */
.mb select,.mb input[type="text"],.mb input[type="date"],
#order-pax,#order-music,#order-tip,#order-date,#order-time-h,#order-time-m,
#loc-picker-link,.srch input{
  background:transparent!important;border:1px solid var(--m3-outline)!important;
  border-radius:var(--m3-sm)!important;color:var(--m3-on-surface)!important;
  font-size:16px!important;padding:14px 16px!important;
  transition:border-color var(--m3-short) var(--m3-std)}
.mb select:focus,.mb input:focus,.srch input:focus{
  outline:none!important;border-color:var(--m3-primary)!important;border-width:2px!important}
.mb label{font-size:12px!important;font-weight:600!important;letter-spacing:.04em!important;
  color:var(--m3-on-surface-var)!important;margin-bottom:6px!important}

/* ═══ LIST ITEMS: взимане / дестинация ═══ */
div:has(> #from-text),div:has(> #to-text){
  background:var(--m3-sc)!important;border:none!important;
  border-radius:var(--m3-md)!important;padding:14px 14px 14px 16px!important;
  font-size:15px!important;font-weight:500!important;margin-bottom:8px!important}

/* ═══ BUTTONS ═══ */
/* filled */
.mcall,#btn-to-change,#btn-picker-confirm{
  background:var(--m3-primary)!important;color:var(--m3-on-primary)!important;
  border:none!important;border-radius:var(--m3-full)!important;
  font-size:15px!important;font-weight:600!important;letter-spacing:.01em!important;
  padding:14px 24px!important;position:relative;overflow:hidden;
  transition:box-shadow var(--m3-short) var(--m3-std)}
.mcall{padding:16px 24px!important;font-size:16px!important}
#btn-to-change,#btn-picker-confirm{padding:10px 20px!important;font-size:14px!important}
/* tonal */
.mvib,#btn-from-change,#btn-picker-gps,#rate-btn,.bc,.bv{
  border:none!important;border-radius:var(--m3-full)!important;
  font-size:14px!important;font-weight:600!important;letter-spacing:.01em!important;
  padding:12px 20px!important;position:relative;overflow:hidden}
#btn-from-change,#btn-picker-gps,#rate-btn{
  background:var(--m3-secondary-c)!important;color:var(--m3-on-secondary-c)!important}
.bc{background:var(--m3-primary)!important;color:var(--m3-on-primary)!important;padding:12px!important}
.bv{background:var(--m3-secondary-c)!important;color:var(--m3-on-secondary-c)!important;padding:12px!important}
.mcall::before,.mvib::before,.bc::before,.bv::before,
#btn-from-change::before,#btn-to-change::before,#rate-btn::before{
  content:'';position:absolute;inset:0;background:#000;opacity:0;
  transition:opacity var(--m3-short) var(--m3-std)}
.mcall:active::before,.mvib:active::before,.bc:active::before,.bv:active::before,
#btn-from-change:active::before,#btn-to-change:active::before,#rate-btn:active::before{opacity:.12}
.mbtns{gap:8px}

/* ═══ BOTTOM SHEET ═══ */
.modal{background:var(--m3-scrim)}
.mb{background:var(--m3-sc-low)!important;border-top:none!important;
  border-radius:var(--m3-xl) var(--m3-xl) 0 0!important;padding:0 20px 24px!important;
  backdrop-filter:none!important;
  animation:m3Sheet var(--m3-long) var(--m3-emph)}
@keyframes m3Sheet{from{transform:translateY(6%);opacity:.4}to{transform:none;opacity:1}}
.m3-handle{position:sticky;top:0;z-index:5;height:26px;
  background:var(--m3-sc-low);margin:0 -20px 4px;display:flex;
  align-items:center;justify-content:center}
.m3-handle::after{content:'';width:32px;height:4px;border-radius:2px;
  background:var(--m3-outline-var)}
.mc{background:var(--m3-sc-high);color:var(--m3-on-surface-var);width:40px;height:40px;
  line-height:40px;font-size:18px}
.mav{width:88px;height:88px;border-radius:var(--m3-lg);border:none;
  background:var(--m3-sc-highest)}
.mn{font-size:24px;font-weight:500;letter-spacing:0;color:var(--m3-on-surface)}
.mc2{font-size:14px;color:var(--m3-on-surface-var)}
.mh{font-size:11px;font-weight:700;letter-spacing:.11em;color:var(--m3-primary);
  border-bottom:none;margin:20px 0 8px;padding-bottom:0}

/* ═══ TAGS: без заливки, само очертание ═══ */
.t{background:transparent!important;border-radius:var(--m3-xs);padding:4px 10px;
  font-size:12px;font-weight:600;border-color:var(--m3-outline-var)!important}
.tb,.tc,.tp,.to,.tpi,.tr{color:var(--m3-on-surface-var)!important}
.vb{color:var(--m3-success)!important;background:var(--m3-success-c)!important;
  border:none!important;border-radius:var(--m3-xs);padding:3px 8px;font-weight:700}
.pi2{background:transparent;border-color:var(--m3-outline-var)}
.founder{animation:none!important;background:var(--m3-primary-c)!important;
  color:var(--m3-on-primary-c)!important;border-radius:var(--m3-xs);font-weight:700}

/* ═══ ГЕРОЯТ ═══ */
#simple-hero{background:var(--m3-sc-low)!important;border-bottom:none!important;
  padding:14px 16px 16px!important}
#simple-hero>button{background:var(--m3-primary)!important;color:var(--m3-on-primary)!important;
  border-radius:var(--m3-xl)!important;padding:18px 24px!important;
  font-size:17px!important;font-weight:600!important;letter-spacing:.01em!important;
  box-shadow:none!important}
#simple-hero>button div{color:var(--m3-on-primary)!important;opacity:.72}
#simple-hero button::after{display:none!important}

/* ═══ ТИШИНА: старите безкрайни анимации отпадат ═══ */
.spark{display:none}
.hint-tabs{animation:none}
.hint-photo::after{animation:none}
.fs:first-of-type .flt:nth-of-type(1),
.fs:first-of-type .flt:nth-of-type(2){animation:none}

/* ═══ ЕДИНСТВЕНОТО движение: списъкът се подрежда веднъж ═══ */
@keyframes m3In{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.dlist .dc,#map-list .dc{animation:m3In var(--m3-med) var(--m3-emph) both}
.dlist .dc:nth-child(1),#map-list .dc:nth-child(1){animation-delay:.02s}
.dlist .dc:nth-child(2),#map-list .dc:nth-child(2){animation-delay:.06s}
.dlist .dc:nth-child(3),#map-list .dc:nth-child(3){animation-delay:.1s}
.dlist .dc:nth-child(n+4),#map-list .dc:nth-child(n+4){animation-delay:.14s}

@media (prefers-reduced-motion:reduce){
  .dlist .dc,#map-list .dc,.mb,.tab.on::after{animation:none}
}
"""

rep('\n</style>\n', CSS + '\n</style>\n', 'M3 слой')

io.open(p, 'w', encoding='utf-8').write(s)
print('OK  %d -> %d chars' % (n0, len(s)))
