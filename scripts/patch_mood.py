# -*- coding: utf-8 -*-
# fish.taxi · нощта става по-тъмна, емблемата следва темата (v4)
#
# 1. По-дълбока нощна схема — повърхностите слизат надолу, контрастът
#    остава четим, жълтото е с един тон по-приглушено. Такси нощем
#    се гледа на тъмна улица, не в офис.
# 2. Емблемата: златното на черно е за нощта, светлата версия — за деня.
#    Прави се с CSS фон, не с JavaScript — сменя се в същия кадър
#    като темата, без премигване.
#
# Пуска се СЛЕД patch_design.py. Идемпотентен.
import io, sys

p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
s = io.open(p, encoding='utf-8').read()
n0 = len(s)

if 'FT-MOOD-V4' in s:
    print('SKIP: mood patch already applied'); sys.exit(0)

def rep(old, new, tag, expect=1):
    global s
    if s.count(old) != expect:
        print('FAIL anchor (%d hits, expected %d): %s' % (s.count(old), expect, tag))
        sys.exit(1)
    s = s.replace(old, new)
    print(' -', tag)

# ── Емблемата: от <img> към елемент с фон, за да се сменя по тема ───
rep(
    '<img src="img/header_logo.png" style="height:44px;object-fit:contain;display:block" alt="fish.taxi">',
    '<a class="ft-logo" href="./" aria-label="fish.taxi"></a>',
    'емблемата следва темата'
)

CSS = u"""
/* ═══════════════ FT-MOOD-V4 ═══════════════ */

/* ── по-дълбока нощ ── */
[data-theme="dark"]{
  --m3-primary:#dcb03a;        --m3-on-primary:#2c2000;
  --m3-primary-c:#4a3600;      --m3-on-primary-c:#f7d886;
  --m3-secondary-c:#3d382c;    --m3-on-secondary-c:#ddd3c0;
  --m3-surface:#0c0b07;        --m3-on-surface:#ded5c6;
  --m3-surface-dim:#0c0b07;
  --m3-sc-lowest:#060502;      --m3-sc-low:#121009;
  --m3-sc:#17140d;             --m3-sc-high:#201c14;
  --m3-sc-highest:#29241b;
  --m3-on-surface-var:#b3a996; --m3-outline:#7b7263;
  --m3-outline-var:#39352c;
  --m3-success:#7cc79c;        --m3-success-c:#123f28;
  --m3-scrim:rgba(0,0,0,.74);
  --m3-state:#ded5c6;
}
/* нощем картата пада още малко, за да не блести в очите */
[data-theme="dark"] .leaflet-tile-pane{
  filter:invert(1) hue-rotate(180deg) brightness(.82) contrast(.9) saturate(.62);
}
[data-theme="dark"] .leaflet-container{background:#07080b!important}
/* табелата остава светла — тя е физически предмет, не част от темата */

/* ── емблемата ── */
.ft-logo{display:block;width:100px;height:46px;flex-shrink:0;
  background:url("img/logo.png") left center/contain no-repeat}
[data-theme="dark"] .ft-logo{width:104px;
  background-image:url("img/header_logo.png")}
"""

rep('\n</style>\n', CSS + '\n</style>\n', 'нощна схема + емблема')

io.open(p, 'w', encoding='utf-8').write(s)
print('OK  %d -> %d chars' % (n0, len(s)))
