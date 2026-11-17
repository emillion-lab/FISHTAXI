#!/usr/bin/env python3
"""FT-DE-V1 (17.11.2026): стандартен немски (de) за fish.taxi, на „du“ като в join-i18n.

Блокът "de" влиза в lib/app-i18n.js пред "gsw". Имената и знамето за de вече са в
app-core.js; поръчката към шофьор вече има OT.de. Идемпотентен."""
import io, json, sys

S = {
 "nearT": "Fahrer in der Nähe", "free": "freie Fahrer in der Nähe", "free1": "freier Fahrer in der Nähe",
 "none": "Keine Fahrer in der Nähe", "nearN": "Fahrer in der Nähe", "near1": "Fahrer in der Nähe",
 "offHint": "Fahrer müssen nicht online sein – du kannst auch bei einem Offline-Fahrer bestellen und dich direkt absprechen.",
 "online": "online", "offline": "offline", "updated": "aktualisiert", "now": "jetzt", "ago": "vor",
 "sec": "s", "min": "Min", "km": "km", "slide": "Wischen für ein Taxi", "fOn": "Nur online",
 "fEn": "Englisch", "fChild": "Kindersitz", "fCard": "Karte", "fPet": "Tiere", "fEv": "Elektro",
 "fBig": "6+ Sitze", "call": "Anrufen", "details": "Fotos & Details", "orderAt": "Bestellen bei",
 "other": "In anderen Städten", "noMatch": "Kein Fahrer mit diesen Filtern. Entferne einen Filter.",
 "car": "Auto", "plate": "Kennzeichen", "seats": "Sitze", "pay": "Zahlung", "tariff": "Tarif", "start": "Grundpreis",
 "day": "Tag", "night": "Nacht", "music": "Musik", "langs": "Sprachen", "pets": "Haustiere",
 "child": "Kindersitz", "airport": "Flughafen", "longd": "Langstrecken", "nightw": "Nachts",
 "wheel": "Rollstuhl", "areas": "Gebiete", "phone": "Telefon", "yes": "Ja", "no": "Nein",
 "ask": "Auf Anfrage", "cash": "Bar", "terminal": "Karte (POS)", "revolut": "Revolut", "onreq": "Auf Anfrage",
 "anyMusic": "Nach Wahl", "noMusic": "Keine Musik", "xEv": "Elektrisch", "xAc": "Klimaanlage",
 "xUsb": "USB-Ladegerät", "xStream": "Musik vom Handy", "xRoof": "Panoramadach",
 "xLeg": "Beinfreiheit", "xTint": "Getönte Scheiben", "xNos": "Nichtraucher",
 "xQuiet": "Ruhige Fahrt auf Wunsch", "xVer": "Verifizierter Fahrer", "share": "Teilen",
 "copied": "Link kopiert.", "oTitle": "Bestellung bei", "pickup": "Abholung", "locOk": "Mein Standort",
 "locWait": "Ich suche dich…", "locNo": "Kein GPS. Schick die Adresse im Chat.", "retry": "Nochmal versuchen",
 "when": "Wann", "wNow": "Jetzt", "wLater": "Später", "pax": "Fahrgäste", "wishes": "Wünsche",
 "pQuiet": "Ruhe", "pTalk": "Gespräch", "pCalm": "Ruhige Fahrweise", "pMusic": "Musik",
 "pBag": "Großes Gepäck", "dest": "Ziel (optional)", "destPh": "Adresse oder Ort", "sms": "SMS senden",
 "wa": "WhatsApp", "viber": "Viber", "vCopied": "Bestellung kopiert. Füge sie im Viber-Chat ein.",
 "notOnline": "Nicht online, aber du kannst bestellen und dich direkt absprechen – er antwortet, sobald er es sieht.",
 "noDrivers": "Keine Fahrer in der Nähe.", "menu": "Menü", "join": "Fahrer werden", "profil": "Mein Profil",
 "profilS": "für Fahrer", "classic": "Alte Seite", "lang": "Sprache",
 "about": "Direkter Kontakt zum Fahrer, ohne Provision.", "osm": "Karte: © OpenStreetMap",
 "locDenied": "Kein Zugriff auf deinen Standort.",
}
X = {
 "Finding routes…": "Suche Routen…",
 "No route to this point. Try a bit closer to a road.": "Keine Route zu diesem Punkt. Versuch es etwas näher an einer Straße.",
 "⚡ Fastest": "⚡ Schnellste", "📏 Shortest": "📏 Kürzeste", "📏 and shortest": "📏 und kürzeste",
 "Other route": "Andere Route", "Close": "Schließen", "Where to": "Wohin",
 "from the centre (no GPS)": "vom Zentrum aus (kein GPS)", "Order to here": "Bis hierher bestellen",
 "No driver nearby.": "Kein Fahrer in der Nähe.",
 "Routing server unavailable — straight-line estimate.": "Routenserver nicht verfügbar – Schätzung per Luftlinie.",
 "Times assume normal traffic, not live.": "Zeiten bei normalem Verkehr, nicht live.",
 "Choose a driver": "Fahrer wählen", "Online and offline — agree directly": "Online und offline – direkt absprechen",
 "Back": "Zurück", "Choose a driver to": "Fahrer wählen für die Fahrt nach", "min away": "Min entfernt",
 "online": "online", "offline": "offline", "seats": "Sitze",
 "Price uses the driver's tariff for the chosen route.": "Der Preis folgt dem Tarif des Fahrers für die gewählte Route.",
 "Press and hold on the map to choose where to": "Halte die Karte gedrückt, um das Ziel zu wählen",
 "📍 Use my location": "📍 Meinen Standort verwenden", "My location or another address": "Mein Standort oder eine andere Adresse",
 "Passenger — name and phone (optional)": "Fahrgast – Name und Telefon (optional)",
 "Day mode — tap for night": "Tagmodus – tippen für Nacht", "Night mode — tap for day": "Nachtmodus – tippen für Tag",
 "☀️ Day mode · tap the logo for night": "☀️ Tagmodus · Logo antippen für Nacht",
 "🌙 Night mode · tap the logo for day": "🌙 Nachtmodus · Logo antippen für Tag",
 "Full screen: ": "Vollbild: ", "on": "an", "off": "aus", "hides the top bar": "blendet die obere Leiste aus",
 "Contact QR.<br>Tap for full screen": "QR für den Kontakt.<br>Tippen für Vollbild",
 "Tap to close": "Zum Schließen tippen", "Privacy": "Datenschutz", "Classical": "Klassik", "Electronic": "Elektronisch",
 "No connection. Reload the page.": "Keine Verbindung. Lade die Seite neu.",
 "taxi straight from the driver": "Taxi direkt vom Fahrer", "Map": "Karte",
 "National Palace of Culture, Sofia": "Nationaler Kulturpalast, Sofia", "Sofia Airport": "Flughafen Sofia",
 "Terminal 1 and 2, Sofia": "Terminal 1 und 2, Sofia", "Central Railway Station": "Hauptbahnhof", "Sofia": "Sofia",
 "Serdika Bus Station": "Busbahnhof Serdika", "Central bus station, Sofia": "Zentraler Busbahnhof, Sofia",
 "Alexander Nevsky Cathedral": "Alexander-Newski-Kathedrale",
 "Cherni Vrah Blvd, Sofia": "Cherni-Vrah-Boulevard, Sofia",
 "Vasil Levski National Stadium": "Nationalstadion Vasil Levski",
}

P = 'lib/app-i18n.js'
s = io.open(P, encoding='utf-8').read()
if '"de":{"S":' in s:
    print(P, ': вече има de — SKIP'); sys.exit(0)
anchor = ',"gsw":{"S":'
if s.count(anchor) != 1:
    print('котвата gsw не е точно веднъж:', s.count(anchor)); sys.exit(1)
block = json.dumps({"de": {"S": S, "X": X}}, ensure_ascii=False, separators=(',', ':'))[1:-1]
s = s.replace(anchor, ',' + block + anchor)
io.open(P, 'w', encoding='utf-8', newline='').write(s)
print(P, ': de добавен')
