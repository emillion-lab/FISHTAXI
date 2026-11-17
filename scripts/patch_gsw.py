#!/usr/bin/env python3
"""FT-GSW-V1 (17.11.2026): швейцарски немски (gsw, Züridütsch-ориентиран) за fish.taxi.

Добавя блок "gsw" в lib/app-i18n.js, име + знаме в lib/app-core.js, десетична точка
(в Швейцария е точка, не запетая) и вдига ?v= на скриптовете в index.html и app.html.
Идемпотентен; всяка котва трябва да е точно веднъж."""
import io, json, sys

def rd(p):
    return io.open(p, encoding='utf-8').read()

def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)

S = {
 "nearT": "Fahrer i de Nööchi", "free": "freii Fahrer i de Nööchi", "free1": "freie Fahrer i de Nööchi",
 "none": "Kei Fahrer i de Nööchi", "nearN": "Fahrer i de Nööchi", "near1": "Fahrer i de Nööchi",
 "offHint": "D Fahrer mönd nöd online si – du chasch au bi emene Offline-Fahrer bstelle und dir diräkt abmache.",
 "online": "online", "offline": "offline", "updated": "aktualisiert", "now": "jetzt", "ago": "vor",
 "sec": "s", "min": "Min", "km": "km", "slide": "Schieb für es Taxi", "fOn": "Nume online",
 "fEn": "Änglisch", "fChild": "Chindersitz", "fCard": "Charte", "fPet": "Tier", "fEv": "Elektrisch",
 "fBig": "6+ Plätz", "call": "Aalüüte", "details": "Fotis und Details", "orderAt": "Bstell bi",
 "other": "I andere Stedt", "noMatch": "Kein Fahrer mit dene Filter. Nimm en Filter wäg.",
 "car": "Auto", "plate": "Nummere", "seats": "Plätz", "pay": "Zahlig", "tariff": "Tarif", "start": "Start",
 "day": "Tag", "night": "Nacht", "music": "Musig", "langs": "Sprache", "pets": "Haustier",
 "child": "Chindersitz", "airport": "Flughafe", "longd": "Lang Fahrte", "nightw": "Znacht",
 "wheel": "Rollstuehl", "areas": "Gebiet", "phone": "Telefon", "yes": "Jo", "no": "Nei",
 "ask": "Uf Aafrag", "cash": "Bar", "terminal": "Charte (POS)", "revolut": "Revolut", "onreq": "Uf Aafrag",
 "anyMusic": "Du wählsch", "noMusic": "Kei Musig", "xEv": "Elektrisch", "xAc": "Klimaanlag",
 "xUsb": "USB-Lader", "xStream": "Musig vo dim Handy", "xRoof": "Panoramadach",
 "xLeg": "Platz für d Bei", "xTint": "Abgedunklet Schiibe", "xNos": "Nichtraucher",
 "xQuiet": "Ruhigi Fahrt uf Wunsch", "xVer": "Verifizierte Fahrer", "share": "Teile",
 "copied": "Link kopiert.", "oTitle": "Bstellig bi", "pickup": "Abholig", "locOk": "Mi Standort",
 "locWait": "Ich suech dich…", "locNo": "Kei GPS. Schick d Adrässe im Chat.", "retry": "Nomol versueche",
 "when": "Wänn", "wNow": "Jetzt", "wLater": "Spöter", "pax": "Passagier", "wishes": "Wünsch",
 "pQuiet": "Ruhe", "pTalk": "Plaudere", "pCalm": "Ruhigi Fahrwiis", "pMusic": "Musig",
 "pBag": "Gross Gepäck", "dest": "Wohii (optional)", "destPh": "Adrässe oder Ort", "sms": "SMS schicke",
 "wa": "WhatsApp", "viber": "Viber", "vCopied": "Bstellig kopiert. Füeg si im Viber-Chat ii.",
 "notOnline": "Nöd online, aber du chasch bstelle und diräkt abmache – er antwortet, sobald er's gseht.",
 "noDrivers": "Kei Fahrer i de Nööchi.", "menu": "Menü", "join": "Wärde Fahrer", "profil": "Mis Profil",
 "profilS": "für Fahrer", "classic": "Alti Site", "lang": "Sprach",
 "about": "Diräkte Kontakt zum Fahrer, ohni Kommission.", "osm": "Charte: © OpenStreetMap",
 "locDenied": "Kei Zuegriff uf din Standort.",
}
X = {
 "Finding routes…": "Ich suech Routene…",
 "No route to this point. Try a bit closer to a road.": "Kei Route zu dem Punkt. Probier's echli necher bi ere Strass.",
 "⚡ Fastest": "⚡ Am schnällschte", "📏 Shortest": "📏 Am churzschte", "📏 and shortest": "📏 und am churzschte",
 "Other route": "Anderi Route", "Close": "Zue", "Where to": "Wohii",
 "from the centre (no GPS)": "vom Zentrum us (kei GPS)", "Order to here": "Bis da bstelle",
 "No driver nearby.": "Kei Fahrer i de Nööchi.",
 "Routing server unavailable — straight-line estimate.": "Routeserver nöd verfüegbar – Schätzig i de Luftlinie.",
 "Times assume normal traffic, not live.": "Zyte gälte für normale Verchehr, nöd live.",
 "Choose a driver": "Wähl en Fahrer", "Online and offline — agree directly": "Online und offline – diräkt abmache",
 "Back": "Zrugg", "Choose a driver to": "Wähl en Fahrer bis", "min away": "Min ewäg",
 "online": "online", "offline": "offline", "seats": "Plätz",
 "Price uses the driver's tariff for the chosen route.": "De Pris folgt em Tarif vom Fahrer für di gwählt Route.",
 "Press and hold on the map to choose where to": "Halt d Charte gedrückt, zum s Ziel uswähle",
 "📍 Use my location": "📍 Mi Standort bruuche", "My location or another address": "Mi Standort oder en andri Adrässe",
 "Passenger — name and phone (optional)": "Passagier – Name und Telefon (optional)",
 "Day mode — tap for night": "Tagmodus – tipp für Nacht", "Night mode — tap for day": "Nachtmodus – tipp für Tag",
 "☀️ Day mode · tap the logo for night": "☀️ Tagmodus · tipp ufs Logo für Nacht",
 "🌙 Night mode · tap the logo for day": "🌙 Nachtmodus · tipp ufs Logo für Tag",
 "Full screen: ": "Vollbild: ", "on": "aa", "off": "uus", "hides the top bar": "versteckt d Leischte obe",
 "Contact QR.<br>Tap for full screen": "QR für de Kontakt.<br>Tipp für Vollbild",
 "Tap to close": "Tipp zum Schliesse", "Privacy": "Datenschutz", "Classical": "Klassik", "Electronic": "Elektronisch",
 "No connection. Reload the page.": "Kei Verbindig. Lad d Site nomol.",
 "taxi straight from the driver": "Taxi diräkt vom Fahrer", "Map": "Charte",
 "National Palace of Culture, Sofia": "Nationale Kulturpalast, Sofia", "Sofia Airport": "Flughafe Sofia",
 "Terminal 1 and 2, Sofia": "Terminal 1 und 2, Sofia", "Central Railway Station": "Hauptbahnhof", "Sofia": "Sofia",
 "Serdika Bus Station": "Busbahnhof Serdika", "Central bus station, Sofia": "Zentrale Busbahnhof, Sofia",
 "Alexander Nevsky Cathedral": "Alexander-Newski-Kathedrale",
 "Cherni Vrah Blvd, Sofia": "Cherni-Vrah-Boulevard, Sofia",
 "Vasil Levski National Stadium": "Nationalstadion Vasil Levski",
}

def one(s, old, new, what):
    n = s.count(old)
    if n != 1:
        print('котвата "%s" не е точно веднъж: %d' % (what, n)); sys.exit(1)
    return s.replace(old, new)

# 1) lib/app-i18n.js — нов блок след френския
P = 'lib/app-i18n.js'
s = rd(P)
if '"gsw":{' in s:
    print(P, ': вече има gsw — SKIP')
else:
    block = json.dumps({"gsw": {"S": S, "X": X}}, ensure_ascii=False, separators=(',', ':'))[1:-1]
    s = one(s, '"Stade national Vasil-Levski"}}};', '"Stade national Vasil-Levski"}},' + block + '};', 'край на fr')
    wr(P, s); print(P, ': gsw добавен')

# 2) lib/app-core.js — име, знаме, десетична точка
P = 'lib/app-core.js'
s = rd(P)
if 'FT-GSW-V1' in s:
    print(P, ': вече е приложен — SKIP')
else:
    s = one(s, "es:'Español',cs:", "es:'Español',gsw:'Schwiizerdütsch',cs:", 'LN')
    s = one(s, "nl:'🇳🇱'}", "nl:'🇳🇱',gsw:'🇨🇭'}", 'FLAG')
    s = one(s, "F.dc=function(){return F.lang==='en'?'.':',';};",
            "F.dc=function(){return (F.lang==='en'||F.lang==='gsw')?'.':',';}; /* FT-GSW-V1: в Швейцария десетичният знак е точка */", 'dc')
    wr(P, s); print(P, ': LN, FLAG, dc')

# 3) cache-bust на скриптовете
for P in ('index.html', 'app.html'):
    s = rd(P)
    if 'lib/app-i18n.js?v=2' in s:
        print(P, ': вече е вдигнат — SKIP'); continue
    s = one(s, 'lib/app-i18n.js?v=1', 'lib/app-i18n.js?v=2', P + ' i18n')
    s = one(s, 'lib/app-core.js?v=7', 'lib/app-core.js?v=8', P + ' core')
    wr(P, s); print(P, ': ?v= вдигнат')
print('FT-GSW-V1 готово')
