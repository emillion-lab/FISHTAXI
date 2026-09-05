import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# 1. Бутонът за поръчка се връщаше на твърдо зашит български текст
#    след изпращане, независимо от избрания език.
# ─────────────────────────────────────────────────────────────────────
OLD_BTN = "btn.textContent='ПОРЪЧАЙ СЕГА';"
NEW_BTN = "btn.textContent=(T[lang]||T.en).btnOrderNow||'ORDER NOW';"
n = s.count(OLD_BTN)
if n:
    s = s.replace(OLD_BTN, NEW_BTN)
    report.append(f"order button: {n} occurrence(s) now translated")
elif NEW_BTN in s:
    report.append("order button: already done")
else:
    raise SystemExit("order button anchor not found")

# ─────────────────────────────────────────────────────────────────────
# 2. Гарантираме, че ключът btnOrderNow съществува във ВСЕКИ език.
#    Слагаме го до вече съществуващия btnVibOrd във всеки блок.
# ─────────────────────────────────────────────────────────────────────
LABELS = {
    'en': 'ORDER NOW',
    'bg': 'ПОРЪЧАЙ СЕГА',
    'de': 'JETZT BESTELLEN',
    'fr': 'COMMANDER',
    'ru': 'ЗАКАЗАТЬ',
    'it': 'ORDINA ORA',
    'es': 'PEDIR AHORA',
}
added = 0
for code, label in LABELS.items():
    # намираме началото на езиковия блок:  en:{   bg:{  ...
    m = re.search(r'\n\s{2}' + code + r':\{', s)
    if not m:
        continue
    blk_start = m.end()
    nxt = re.search(r'\n\s{2}[a-z]{2}:\{', s[blk_start:])
    blk_end = blk_start + (nxt.start() if nxt else len(s) - blk_start)
    block = s[blk_start:blk_end]
    if 'btnOrderNow:' in block:
        continue
    anchor = 'btnVibOrd:'
    ai = block.find(anchor)
    if ai < 0:
        continue
    new_block = block[:ai] + 'btnOrderNow:"' + label + '",' + block[ai:]
    s = s[:blk_start] + new_block + s[blk_end:]
    added += 1
report.append(f"btnOrderNow key added to {added} language block(s)")

# ─────────────────────────────────────────────────────────────────────
# 3. Ланселот: широк регион — лятото Ривиерата, зимата Алпите.
# ─────────────────────────────────────────────────────────────────────
OLD_AREAS = '"areas":"Saint-Tropez — French Riviera, Côte d\'Azur",'
NEW_AREAS = ('"areas":"French Riviera & Alps — Nice, Cannes, Saint-Tropez, '
             'Monaco, Marseille · winter: Tarentaise ski resorts",')
if OLD_AREAS in s:
    s = s.replace(OLD_AREAS, NEW_AREAS, 1)
    report.append("areas: widened to Riviera + Alps")
elif NEW_AREAS in s:
    report.append("areas: already done")
else:
    raise SystemExit("areas anchor not found")

OLD_BIO = ('"bio":"VIP transfer service based in Saint-Tropez and the '
           'French Riviera. Mercedes V-Class, 6 leather seats."')
NEW_BIO = ('"bio":"VIP transfers across the French Riviera in summer '
           '(Nice, Cannes, Saint-Tropez, Monaco) and the Alps in winter '
           '(Tarentaise ski resorts). Mercedes V-Class, 7 leather seats. '
           'Airport and long-distance transfers."')
if OLD_BIO in s:
    s = s.replace(OLD_BIO, NEW_BIO, 1)
    report.append("bio: updated (7 seats, both seasons)")
elif NEW_BIO in s:
    report.append("bio: already done")
else:
    report.append("bio: anchor not found — SKIPPED")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
