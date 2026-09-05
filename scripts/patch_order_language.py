import io

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s
report = []

# ─────────────────────────────────────────────────────────────────────
# Езикът на поръчката се съобразява с шофьора.
#
# Правило:
#   клиентът пише на език, който шофьорът говори  -> поръчка на този език
#   иначе                                         -> английски + код на
#                                                    езика на клиента
#
# Така българин, поръчващ на българин, получава български.  Французин
# при Lancelot (fr,en,bg,ru) получава френски.  Испанец при български
# шофьор дава английска поръчка с етикет [ES], за да е ясно откъде идва
# и на какъв език да отговори шофьорът.
#
# Езиците на шофьора са в d.langs — вече съществуват в профила.
# ─────────────────────────────────────────────────────────────────────

HELPER = '''
/* Език за текста на поръчката: съвпадение с езиците на шофьора,
   иначе английски.  Виж ORDER_T по-долу за самите текстове.     */
function orderLang(d){
  var dl=(d&&d.langs)||[];
  return dl.indexOf(lang)>=0 ? lang : 'en';
}
/* Кодът на езика, на който КЛИЕНТЪТ ползва приложението.
   Показва се само когато не съвпада с езика на поръчката —
   за да знае шофьорът на какъв език да отговори.               */
function clientLangTag(d){
  return orderLang(d)===lang ? '' : ' ['+String(lang).toUpperCase()+']';
}
var ORDER_T={
 bg:{head:'\\u{1F695} fish.taxi \\u2014 \\u0411\\u042A\\u0420\\u0417\\u0410 \\u041F\\u041E\\u0420\\u042A\\u0427\\u041A\\u0410',now:'\\u{1F552} \\u0421\\u0435\\u0433\\u0430 (\\u0432\\u0435\\u0434\\u043D\\u0430\\u0433\\u0430)',pax:'\\u2022 \\u041F\\u044A\\u0442\\u043D\\u0438\\u0446\\u0438: ',prefs:'\\u041F\\u0440\\u0435\\u0434\\u043F\\u043E\\u0447\\u0438\\u0442\\u0430\\u043D\\u0438\\u044F:',myloc:'\\u{1F4CD} \\u041C\\u043E\\u044F\\u0442\\u0430 \\u043B\\u043E\\u043A\\u0430\\u0446\\u0438\\u044F:',nogps:'\\u{1F4CD} \\u041B\\u043E\\u043A\\u0430\\u0446\\u0438\\u044F: \\u0449\\u0435 \\u044F \\u043F\\u0440\\u0430\\u0442\\u044F \\u0432 \\u0447\\u0430\\u0442\\u0430 (GPS \\u043E\\u0442\\u043A\\u0430\\u0437\\u0430\\u043D)',confirm:'\\u260E\\uFE0F \\u041F\\u043E\\u0442\\u0432\\u044A\\u0440\\u0436\\u0434\\u0435\\u043D\\u0438\\u0435 \\u043D\\u0430 \\u0442\\u043E\\u0437\\u0438 \\u043D\\u043E\\u043C\\u0435\\u0440.'},
 en:{head:'\\u{1F695} fish.taxi \\u2014 QUICK ORDER',now:'\\u{1F552} Now (immediately)',pax:'\\u2022 Passengers: ',prefs:'Preferences:',myloc:'\\u{1F4CD} My location:',nogps:'\\u{1F4CD} Location: will send in chat (GPS denied)',confirm:'\\u260E\\uFE0F Confirm on this number.'},
 de:{head:'\\u{1F695} fish.taxi \\u2014 SCHNELLBESTELLUNG',now:'\\u{1F552} Jetzt (sofort)',pax:'\\u2022 Fahrg\\u00E4ste: ',prefs:'W\\u00FCnsche:',myloc:'\\u{1F4CD} Mein Standort:',nogps:'\\u{1F4CD} Standort: sende ich im Chat (GPS abgelehnt)',confirm:'\\u260E\\uFE0F Best\\u00E4tigung unter dieser Nummer.'},
 fr:{head:'\\u{1F695} fish.taxi \\u2014 COMMANDE RAPIDE',now:'\\u{1F552} Maintenant (imm\\u00E9diatement)',pax:'\\u2022 Passagers : ',prefs:'Pr\\u00E9f\\u00E9rences :',myloc:'\\u{1F4CD} Ma position :',nogps:'\\u{1F4CD} Position : je l\\u2019envoie dans le chat (GPS refus\\u00E9)',confirm:'\\u260E\\uFE0F Confirmation \\u00E0 ce num\\u00E9ro.'},
 ru:{head:'\\u{1F695} fish.taxi \\u2014 \\u0411\\u042B\\u0421\\u0422\\u0420\\u042B\\u0419 \\u0417\\u0410\\u041A\\u0410\\u0417',now:'\\u{1F552} \\u0421\\u0435\\u0439\\u0447\\u0430\\u0441 (\\u0441\\u0440\\u0430\\u0437\\u0443)',pax:'\\u2022 \\u041F\\u0430\\u0441\\u0441\\u0430\\u0436\\u0438\\u0440\\u044B: ',prefs:'\\u041F\\u043E\\u0436\\u0435\\u043B\\u0430\\u043D\\u0438\\u044F:',myloc:'\\u{1F4CD} \\u041C\\u043E\\u0451 \\u043C\\u0435\\u0441\\u0442\\u043E\\u043F\\u043E\\u043B\\u043E\\u0436\\u0435\\u043D\\u0438\\u0435:',nogps:'\\u{1F4CD} \\u041C\\u0435\\u0441\\u0442\\u043E: \\u043F\\u0440\\u0438\\u0448\\u043B\\u044E \\u0432 \\u0447\\u0430\\u0442 (GPS \\u043E\\u0442\\u043A\\u043B\\u043E\\u043D\\u0451\\u043D)',confirm:'\\u260E\\uFE0F \\u041F\\u043E\\u0434\\u0442\\u0432\\u0435\\u0440\\u0436\\u0434\\u0435\\u043D\\u0438\\u0435 \\u043D\\u0430 \\u044D\\u0442\\u043E\\u0442 \\u043D\\u043E\\u043C\\u0435\\u0440.'},
 it:{head:'\\u{1F695} fish.taxi \\u2014 ORDINE RAPIDO',now:'\\u{1F552} Ora (subito)',pax:'\\u2022 Passeggeri: ',prefs:'Preferenze:',myloc:'\\u{1F4CD} La mia posizione:',nogps:'\\u{1F4CD} Posizione: la invio in chat (GPS negato)',confirm:'\\u260E\\uFE0F Conferma a questo numero.'},
 es:{head:'\\u{1F695} fish.taxi \\u2014 PEDIDO R\\u00C1PIDO',now:'\\u{1F552} Ahora (inmediatamente)',pax:'\\u2022 Pasajeros: ',prefs:'Preferencias:',myloc:'\\u{1F4CD} Mi ubicaci\\u00F3n:',nogps:'\\u{1F4CD} Ubicaci\\u00F3n: la enviar\\u00E9 en el chat (GPS denegado)',confirm:'\\u260E\\uFE0F Confirmaci\\u00F3n a este n\\u00FAmero.'}
};
function orderT(d){ return ORDER_T[orderLang(d)]||ORDER_T.en; }
'''

if 'function orderLang' not in s:
    anchor = 'function pickOnlineDriver()'
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("pickOnlineDriver anchor not found")
    s = s[:i] + HELPER.lstrip('\n') + '\n' + s[i:]
    report.append("orderLang + ORDER_T table added (7 languages)")
else:
    report.append("order language helpers: already there")

# ── Пренаписваме строенето на съобщението ───────────────────────────
OLD = """    var lines=['\U0001F695 fish.taxi — \u0411\u042a\u0420\u0417\u0410 \u041f\u041e\u0420\u042a\u0427\u041a\u0410','','\U0001F552 \u0421\u0435\u0433\u0430 (\u0432\u0435\u0434\u043d\u0430\u0433\u0430)'];
    var p=getPrefs();
    if(p){
      if(p.pax)lines.push('\u2022 \u041f\u044a\u0442\u043d\u0438\u0446\u0438: '+p.pax);
      if(p.tags&&p.tags.length){lines.push('\u041f\u0440\u0435\u0434\u043f\u043e\u0447\u0438\u0442\u0430\u043d\u0438\u044f:');p.tags.forEach(function(t){if(PREF_LABELS[t])lines.push('\u2022 '+PREF_LABELS[t]);});}
    }
    lines.push('');
    if(lat&&lng){lines.push('\U0001F4CD \u041c\u043e\u044f\u0442\u0430 \u043b\u043e\u043a\u0430\u0446\u0438\u044f:');lines.push('https://maps.google.com/?q='+lat+','+lng);}
    else{lines.push('\U0001F4CD \u041b\u043e\u043a\u0430\u0446\u0438\u044f: \u0449\u0435 \u044f \u043f\u0440\u0430\u0442\u044f \u0432 \u0447\u0430\u0442\u0430 (GPS \u043e\u0442\u043a\u0430\u0437\u0430\u043d)');}
    lines.push('');lines.push('\u260E\uFE0F \u041f\u043e\u0442\u0432\u044a\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u043d\u0430 \u0442\u043e\u0437\u0438 \u043d\u043e\u043c\u0435\u0440.');"""

NEW = """    var ot=orderT(d);
    var lines=[ot.head+clientLangTag(d),'',ot.now];
    var p=getPrefs();
    if(p){
      if(p.pax)lines.push(ot.pax+p.pax);
      if(p.tags&&p.tags.length){lines.push(ot.prefs);p.tags.forEach(function(t){if(PREF_LABELS[t])lines.push('\u2022 '+PREF_LABELS[t]);});}
    }
    lines.push('');
    if(lat&&lng){lines.push(ot.myloc);lines.push('https://maps.google.com/?q='+lat+','+lng);}
    else{lines.push(ot.nogps);}
    lines.push('');lines.push(ot.confirm);"""

if OLD in s:
    s = s.replace(OLD, NEW, 1)
    report.append("order message now uses driver-matched language")
elif 'var ot=orderT(d);' in s:
    report.append("order message: already patched")
else:
    raise SystemExit("order message block not matched")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")

for line in report:
    print(" -", line)
