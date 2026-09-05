import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# Хиро-блокът никога не се превеждаше.
#
# btnOrderNow вече съществуваше в таблицата, но setLang() не пипаше
# бутона — HTML-ът съдържаше зашит български текст, който оставаше
# такъв на всички езици.  Същото за подзаглавието, "Още опции",
# промпта за предпочитания и бутоните в него.
#
# Тук: добавяме липсващите ключове на 7 езика и ги закачаме в setLang.
# ─────────────────────────────────────────────────────────────────────

NEW_KEYS = {
 'en': dict(heroSub='nearest taxi', moreOpts='More options \u2193',
   prefsQ='\U0001F4BE Save preferences for next time? (optional)',
   prefsSave='Save', prefsSkip='No thanks', paxQ='Passengers?',
   pbMusic='\U0001F3B5 Music', noDriver='No driver online right now. Try again shortly.',
   gettingLoc='\U0001F4CD GETTING LOCATION\u2026',
   prefsSaved='\u2705 Saved! Your next order carries your preferences automatically.'),
 'bg': dict(heroSub='\u043d\u0430\u0439-\u0431\u043b\u0438\u0437\u043a\u043e\u0442\u043e \u0442\u0430\u043a\u0441\u0438', moreOpts='\u041e\u0449\u0435 \u043e\u043f\u0446\u0438\u0438 \u2193',
   prefsQ='\U0001F4BE \u0417\u0430\u043f\u0430\u0437\u0438 \u043f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u043d\u0438\u044f \u0437\u0430 \u0441\u043b\u0435\u0434\u0432\u0430\u0449\u0438\u044f \u043f\u044a\u0442? (\u043f\u043e \u0438\u0437\u0431\u043e\u0440)',
   prefsSave='\u0417\u0430\u043f\u0430\u0437\u0438', prefsSkip='\u041d\u0435, \u0431\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u044f', paxQ='\u041f\u044a\u0442\u043d\u0438\u0446\u0438?',
   pbMusic='\U0001F3B5 \u041c\u0443\u0437\u0438\u043a\u0430', noDriver='\u0412 \u043c\u043e\u043c\u0435\u043d\u0442\u0430 \u043d\u044f\u043c\u0430 \u0448\u043e\u0444\u044c\u043e\u0440 \u043d\u0430 \u043b\u0438\u043d\u0438\u044f. \u041e\u043f\u0438\u0442\u0430\u0439 \u0441\u043b\u0435\u0434 \u043c\u0430\u043b\u043a\u043e.',
   gettingLoc='\U0001F4CD \u0412\u0417\u0418\u041c\u0410\u041c \u041b\u041e\u041a\u0410\u0426\u0418\u042f\u0422\u0410\u2026',
   prefsSaved='\u2705 \u0417\u0430\u043f\u0430\u0437\u0435\u043d\u043e! \u0421\u043b\u0435\u0434\u0432\u0430\u0449\u0430\u0442\u0430 \u043f\u043e\u0440\u044a\u0447\u043a\u0430 \u0438\u0434\u0432\u0430 \u0441 \u0442\u0432\u043e\u0438\u0442\u0435 \u043f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u043d\u0438\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u043d\u043e.'),
 'de': dict(heroSub='n\u00e4chstes Taxi', moreOpts='Mehr Optionen \u2193',
   prefsQ='\U0001F4BE Einstellungen f\u00fcr n\u00e4chstes Mal speichern? (optional)',
   prefsSave='Speichern', prefsSkip='Nein danke', paxQ='Fahrg\u00e4ste?',
   pbMusic='\U0001F3B5 Musik', noDriver='Aktuell ist kein Fahrer online. Bitte gleich nochmal versuchen.',
   gettingLoc='\U0001F4CD STANDORT WIRD ERMITTELT\u2026',
   prefsSaved='\u2705 Gespeichert! Die n\u00e4chste Bestellung \u00fcbernimmt deine W\u00fcnsche automatisch.'),
 'fr': dict(heroSub='taxi le plus proche', moreOpts='Plus d\u2019options \u2193',
   prefsQ='\U0001F4BE Enregistrer vos pr\u00e9f\u00e9rences pour la prochaine fois ? (facultatif)',
   prefsSave='Enregistrer', prefsSkip='Non merci', paxQ='Passagers ?',
   pbMusic='\U0001F3B5 Musique', noDriver='Aucun chauffeur en ligne pour le moment. R\u00e9essayez dans un instant.',
   gettingLoc='\U0001F4CD LOCALISATION EN COURS\u2026',
   prefsSaved='\u2705 Enregistr\u00e9 ! Votre prochaine commande reprendra vos pr\u00e9f\u00e9rences automatiquement.'),
 'ru': dict(heroSub='\u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0435\u0435 \u0442\u0430\u043a\u0441\u0438', moreOpts='\u0411\u043e\u043b\u044c\u0448\u0435 \u043e\u043f\u0446\u0438\u0439 \u2193',
   prefsQ='\U0001F4BE \u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u044f \u043d\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0440\u0430\u0437? (\u043d\u0435\u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e)',
   prefsSave='\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c', prefsSkip='\u041d\u0435\u0442, \u0441\u043f\u0430\u0441\u0438\u0431\u043e', paxQ='\u041f\u0430\u0441\u0441\u0430\u0436\u0438\u0440\u044b?',
   pbMusic='\U0001F3B5 \u041c\u0443\u0437\u044b\u043a\u0430', noDriver='\u0421\u0435\u0439\u0447\u0430\u0441 \u043d\u0435\u0442 \u0432\u043e\u0434\u0438\u0442\u0435\u043b\u0435\u0439 \u043e\u043d\u043b\u0430\u0439\u043d. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0447\u0435\u0440\u0435\u0437 \u043c\u0438\u043d\u0443\u0442\u0443.',
   gettingLoc='\U0001F4CD \u041e\u041f\u0420\u0415\u0414\u0415\u041b\u042f\u042e \u041c\u0415\u0421\u0422\u041e\u041f\u041e\u041b\u041e\u0416\u0415\u041d\u0418\u0415\u2026',
   prefsSaved='\u2705 \u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043e! \u0421\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0437\u0430\u043a\u0430\u0437 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u0443\u0447\u0442\u0451\u0442 \u0432\u0430\u0448\u0438 \u043f\u043e\u0436\u0435\u043b\u0430\u043d\u0438\u044f.'),
 'it': dict(heroSub='taxi pi\u00f9 vicino', moreOpts='Altre opzioni \u2193',
   prefsQ='\U0001F4BE Salvare le preferenze per la prossima volta? (facoltativo)',
   prefsSave='Salva', prefsSkip='No grazie', paxQ='Passeggeri?',
   pbMusic='\U0001F3B5 Musica', noDriver='Nessun autista online al momento. Riprova tra poco.',
   gettingLoc='\U0001F4CD RILEVAMENTO POSIZIONE\u2026',
   prefsSaved='\u2705 Salvato! Il prossimo ordine user\u00e0 le tue preferenze automaticamente.'),
 'es': dict(heroSub='taxi m\u00e1s cercano', moreOpts='M\u00e1s opciones \u2193',
   prefsQ='\U0001F4BE \u00bfGuardar preferencias para la pr\u00f3xima vez? (opcional)',
   prefsSave='Guardar', prefsSkip='No, gracias', paxQ='\u00bfPasajeros?',
   pbMusic='\U0001F3B5 M\u00fasica', noDriver='Ahora mismo no hay conductores en l\u00ednea. Int\u00e9ntalo en un momento.',
   gettingLoc='\U0001F4CD OBTENIENDO UBICACI\u00d3N\u2026',
   prefsSaved='\u2705 \u00a1Guardado! Tu pr\u00f3ximo pedido usar\u00e1 tus preferencias autom\u00e1ticamente.'),
}

added = 0
for code, kv in NEW_KEYS.items():
    m = re.search(r'\n\s{2}' + code + r':\{', s)
    if not m:
        report.append(f"lang block {code} NOT FOUND - skipped")
        continue
    blk_start = m.end()
    nxt = re.search(r'\n\s{2}[a-z]{2}:\{', s[blk_start:])
    blk_end = blk_start + (nxt.start() if nxt else len(s) - blk_start)
    block = s[blk_start:blk_end]
    ins = []
    for k, v in kv.items():
        if k + ':' in block:
            continue
        ins.append(k + ':"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"')
    if not ins:
        continue
    anchor = 'btnOrderNow:'
    ai = block.find(anchor)
    if ai < 0:
        report.append(f"{code}: btnOrderNow anchor missing - skipped")
        continue
    new_block = block[:ai] + ','.join(ins) + ',' + block[ai:]
    s = s[:blk_start] + new_block + s[blk_end:]
    added += 1

report.append(f"missing keys added to {added} language block(s)")

# ── setLang вече обновява и хиро-блока ──────────────────────────────
HOOK = '''  /* Хиро-блокът: беше зашит на български и не се превеждаше. */
  var hb=document.getElementById('hero-btn-txt');
  if(hb)hb.textContent=t.btnOrderNow||'ORDER NOW';
  var hs=document.getElementById('hero-btn-sub');
  if(hs)hs.textContent=t.heroSub||'';
  var mo=document.getElementById('hero-more');
  if(mo)mo.textContent=t.moreOpts||'';
  var pq=document.getElementById('prefs-q');
  if(pq)pq.textContent=t.prefsQ||'';
  var psv=document.getElementById('prefs-save');
  if(psv)psv.textContent=t.prefsSave||'';
  var psk=document.getElementById('prefs-skip');
  if(psk)psk.textContent=t.prefsSkip||'';
  var pxq=document.getElementById('prefs-pax-q');
  if(pxq)pxq.textContent=t.paxQ||'';
'''
if "document.getElementById('hero-btn-txt')" not in s.split('function setLang(')[1][:3000]:
    m = re.search(r"function setLang\(l\)\{\n  lang=l;\n  localStorage\.setItem\('fishtaxi-lang',l\);\n  var t=T\[l\]\|\|T\.en;\n", s)
    if not m:
        raise SystemExit("setLang head not matched")
    s = s[:m.end()] + HOOK + s[m.end():]
    report.append("setLang now updates the hero block")
else:
    report.append("setLang hero hook: already there")

# ── Даваме id на елементите, които досега нямаха ────────────────────
SUBS = [
 ('<div style="font-size:11px;font-weight:600;text-transform:lowercase;color:#3a3a3a;margin-top:2px;letter-spacing:.2px">\u043d\u0430\u0439-\u0431\u043b\u0438\u0437\u043a\u043e\u0442\u043e \u0442\u0430\u043a\u0441\u0438</div>',
  '<div id="hero-btn-sub" style="font-size:11px;font-weight:600;text-transform:lowercase;color:#3a3a3a;margin-top:2px;letter-spacing:.2px">\u043d\u0430\u0439-\u0431\u043b\u0438\u0437\u043a\u043e\u0442\u043e \u0442\u0430\u043a\u0441\u0438</div>',
  'hero-btn-sub id'),
 ('style="color:#f0b429">\u041e\u0449\u0435 \u043e\u043f\u0446\u0438\u0438 \u2193</a>',
  'id="hero-more" style="color:#f0b429">\u041e\u0449\u0435 \u043e\u043f\u0446\u0438\u0438 \u2193</a>',
  'hero-more id'),
]
for old, new, label in SUBS:
    if old in s:
        s = s.replace(old, new, 1)
        report.append(label + " added")
    elif new.split('"')[1] in s:
        report.append(label + ": already there")
    else:
        report.append(label + ": anchor NOT FOUND")

# ── Съобщенията в JS вече минават през таблицата ────────────────────
JS_SUBS = [
 ("alert('\u0412 \u043c\u043e\u043c\u0435\u043d\u0442\u0430 \u043d\u044f\u043c\u0430 \u0448\u043e\u0444\u044c\u043e\u0440 \u043d\u0430 \u043b\u0438\u043d\u0438\u044f. \u041e\u043f\u0438\u0442\u0430\u0439 \u0441\u043b\u0435\u0434 \u043c\u0430\u043b\u043a\u043e.')",
  "alert((T[lang]||T.en).noDriver||'No driver online right now.')", 'noDriver alert'),
 ("btn.textContent='\U0001F4CD \u0412\u0417\u0418\u041c\u0410\u041c \u041b\u041e\u041a\u0410\u0426\u0418\u042f\u0422\u0410\u2026';",
  "btn.textContent=(T[lang]||T.en).gettingLoc||'GETTING LOCATION\u2026';", 'gettingLoc'),
 ("document.getElementById('hero-sub').innerHTML='\u2705 \u0417\u0430\u043f\u0430\u0437\u0435\u043d\u043e! \u0421\u043b\u0435\u0434\u0432\u0430\u0449\u0430\u0442\u0430 \u043f\u043e\u0440\u044a\u0447\u043a\u0430 \u0438\u0434\u0432\u0430 \u0441 \u0442\u0432\u043e\u0438\u0442\u0435 \u043f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u043d\u0438\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u043d\u043e.';",
  "document.getElementById('hero-sub').innerHTML=(T[lang]||T.en).prefsSaved||'Saved!';", 'prefsSaved'),
]
for old, new, label in JS_SUBS:
    if old in s:
        s = s.replace(old, new, 1)
        report.append(label + ": translated")
    elif new[:40] in s:
        report.append(label + ": already done")
    else:
        report.append(label + ": anchor NOT FOUND")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
