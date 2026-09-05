#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерира lib/join-i18n.js от речника по-долу.

Езиците живеят тук, в Python, а не в join.html — така добавянето на
нов език е една секция в този файл, а проверката във workflow-а
гарантира, че никой ключ не липсва.

Текстът е нарочно кратък.  Едно послание: нула комисиона, клиентът
звъни директно.  Без обещания за бъдещето.

footBG се попълва САМО за български.  Чуждите шофьори нямат местен
регистър на такситата и не бива да виждат текст за българския.
"""
import json

LANGS = ['bg','en','de','fr','es','it','ru','ro','el','tr','pl','nl']

NAMES = {
 'bg':'Български','en':'English','de':'Deutsch','fr':'Français',
 'es':'Español','it':'Italiano','ru':'Русский','ro':'Română',
 'el':'Ελληνικά','tr':'Türkçe','pl':'Polski','nl':'Nederlands',
}

T = {
'bg': dict(
 lead='Заявка за присъединяване. Под минута.',
 h1='0% комисиона. Печелиш каквото си изкарал.',
 p='Големите платформи взимат 20–40% от всеки курс — при късите най-много. Ние не взимаме нищо. Клиентът те вижда, звъни ти директно, плаща на теб.',
 b1='Без комисиона — нито сега, нито по-късно',
 b2='Клиентът звъни директно на теб',
 b3='Founder значка за първите — постоянна',
 s1='Твоят телефон', ph1='Телефон', hint1='Въведи телефонния си номер',
 s2='Твоят автомобил', ph2='Регистрационен номер', hint2='Въведи поне 3 знака от номера',
 hintF='Колата ще потвърдим ръчно. Опиши я накратко.', phF='Марка, модел, рег. номер',
 s3='Твоето име', ph3='Име и фамилия',
 s4='Изпрати заявката', hint4='Отваря се готово съобщение. Само натискаш „изпрати“.',
 okH='Заявката е изпратена', okP='Ще се свържем с теб до 24 часа.',
 errName='Моля, име и фамилия.',
 gdpr='Показваме на клиентите само това, което сам попълниш тук. Нищо повече.',
 footBG='За български номера данните идват от публичния регистър на ИА „Автомобилна администрация“.',
),
'en': dict(
 lead='Join request. Under a minute.',
 h1='0% commission. You keep what you earn.',
 p='The big platforms take 20–40% of every ride — most on short trips. We take nothing. The client sees you, calls you directly, pays you.',
 b1='No commission — not now, not later',
 b2='Clients call you directly',
 b3='Founder badge for the first drivers — permanent',
 s1='Your phone', ph1='Phone', hint1='Enter your phone number',
 s2='Your car', ph2='Plate number', hint2='Enter at least 3 characters',
 hintF='We verify the car manually. Describe it briefly.', phF='Make, model, plate',
 s3='Your name', ph3='First and last name',
 s4='Send request', hint4='A ready message opens. You just press send.',
 okH='Request sent', okP='We will contact you within 24 hours.',
 errName='Please enter first and last name.',
 gdpr='We show clients only what you fill in here. Nothing more.',
 footBG='',
),
'de': dict(
 lead='Beitrittsanfrage. Unter einer Minute.',
 h1='0 % Provision. Du behältst, was du verdienst.',
 p='Die großen Plattformen nehmen 20–40 % pro Fahrt — bei kurzen Strecken am meisten. Wir nehmen nichts. Der Kunde sieht dich, ruft dich direkt an, zahlt an dich.',
 b1='Keine Provision — jetzt nicht und später nicht',
 b2='Kunden rufen dich direkt an',
 b3='Founder-Abzeichen für die Ersten — dauerhaft',
 s1='Deine Telefonnummer', ph1='Telefon', hint1='Gib deine Telefonnummer ein',
 s2='Dein Fahrzeug', ph2='Kennzeichen', hint2='Mindestens 3 Zeichen eingeben',
 hintF='Wir prüfen das Fahrzeug manuell. Kurz beschreiben.', phF='Marke, Modell, Kennzeichen',
 s3='Dein Name', ph3='Vor- und Nachname',
 s4='Anfrage senden', hint4='Eine fertige Nachricht öffnet sich. Du drückst nur auf Senden.',
 okH='Anfrage gesendet', okP='Wir melden uns innerhalb von 24 Stunden.',
 errName='Bitte Vor- und Nachnamen angeben.',
 gdpr='Kunden sehen nur das, was du hier einträgst. Nichts weiter.',
 footBG='',
),
'fr': dict(
 lead='Demande d’inscription. Moins d’une minute.',
 h1='0 % de commission. Vous gardez ce que vous gagnez.',
 p='Les grandes plateformes prennent 20 à 40 % de chaque course — le plus sur les trajets courts. Nous, rien. Le client vous voit, vous appelle directement, vous paie.',
 b1='Aucune commission — ni maintenant, ni plus tard',
 b2='Les clients vous appellent directement',
 b3='Badge Founder pour les premiers — permanent',
 s1='Votre téléphone', ph1='Téléphone', hint1='Saisissez votre numéro',
 s2='Votre véhicule', ph2='Plaque d’immatriculation', hint2='Saisissez au moins 3 caractères',
 hintF='Nous vérifions le véhicule manuellement. Décrivez-le brièvement.', phF='Marque, modèle, plaque',
 s3='Votre nom', ph3='Nom et prénom',
 s4='Envoyer la demande', hint4='Un message prêt s’ouvre. Vous n’avez qu’à l’envoyer.',
 okH='Demande envoyée', okP='Nous vous contacterons sous 24 heures.',
 errName='Merci d’indiquer nom et prénom.',
 gdpr='Nous montrons aux clients uniquement ce que vous saisissez ici. Rien de plus.',
 footBG='',
),
'es': dict(
 lead='Solicitud de alta. Menos de un minuto.',
 h1='0 % de comisión. Te quedas con lo que ganas.',
 p='Las grandes plataformas se llevan el 20–40 % de cada viaje — más aún en los trayectos cortos. Nosotros, nada. El cliente te ve, te llama directamente y te paga.',
 b1='Sin comisión — ni ahora ni después',
 b2='Los clientes te llaman directamente',
 b3='Insignia Founder para los primeros — permanente',
 s1='Tu teléfono', ph1='Teléfono', hint1='Introduce tu número',
 s2='Tu vehículo', ph2='Matrícula', hint2='Introduce al menos 3 caracteres',
 hintF='Verificamos el coche manualmente. Descríbelo brevemente.', phF='Marca, modelo, matrícula',
 s3='Tu nombre', ph3='Nombre y apellidos',
 s4='Enviar solicitud', hint4='Se abre un mensaje listo. Solo pulsa enviar.',
 okH='Solicitud enviada', okP='Te contactaremos en 24 horas.',
 errName='Introduce nombre y apellidos.',
 gdpr='Mostramos a los clientes solo lo que rellenes aquí. Nada más.',
 footBG='',
),
'it': dict(
 lead='Richiesta di adesione. Meno di un minuto.',
 h1='0% di commissione. Tieni quello che guadagni.',
 p='Le grandi piattaforme prendono il 20–40% di ogni corsa — soprattutto sulle tratte brevi. Noi niente. Il cliente ti vede, ti chiama direttamente, paga te.',
 b1='Nessuna commissione — né ora né dopo',
 b2='I clienti ti chiamano direttamente',
 b3='Badge Founder per i primi — permanente',
 s1='Il tuo telefono', ph1='Telefono', hint1='Inserisci il tuo numero',
 s2='La tua auto', ph2='Targa', hint2='Inserisci almeno 3 caratteri',
 hintF='Verifichiamo l’auto manualmente. Descrivila brevemente.', phF='Marca, modello, targa',
 s3='Il tuo nome', ph3='Nome e cognome',
 s4='Invia richiesta', hint4='Si apre un messaggio pronto. Basta premere invia.',
 okH='Richiesta inviata', okP='Ti contatteremo entro 24 ore.',
 errName='Inserisci nome e cognome.',
 gdpr='Mostriamo ai clienti solo ciò che inserisci qui. Nulla di più.',
 footBG='',
),
'ru': dict(
 lead='Заявка на присоединение. Меньше минуты.',
 h1='0% комиссии. Вы оставляете себе всё, что заработали.',
 p='Крупные платформы берут 20–40% с каждой поездки — на коротких больше всего. Мы не берём ничего. Клиент видит вас, звонит напрямую и платит вам.',
 b1='Без комиссии — ни сейчас, ни потом',
 b2='Клиенты звонят вам напрямую',
 b3='Значок Founder для первых — навсегда',
 s1='Ваш телефон', ph1='Телефон', hint1='Введите номер телефона',
 s2='Ваш автомобиль', ph2='Гос. номер', hint2='Введите минимум 3 символа',
 hintF='Автомобиль проверим вручную. Опишите его кратко.', phF='Марка, модель, номер',
 s3='Ваше имя', ph3='Имя и фамилия',
 s4='Отправить заявку', hint4='Откроется готовое сообщение. Просто нажмите «отправить».',
 okH='Заявка отправлена', okP='Свяжемся с вами в течение 24 часов.',
 errName='Укажите имя и фамилию.',
 gdpr='Клиентам показываем только то, что вы заполнили здесь. Ничего больше.',
 footBG='',
),
'ro': dict(
 lead='Cerere de înscriere. Sub un minut.',
 h1='0% comision. Păstrezi tot ce câștigi.',
 p='Platformele mari iau 20–40% din fiecare cursă — cel mai mult la cursele scurte. Noi nu luăm nimic. Clientul te vede, te sună direct și îți plătește ție.',
 b1='Fără comision — nici acum, nici mai târziu',
 b2='Clienții te sună direct',
 b3='Insignă Founder pentru primii — permanentă',
 s1='Telefonul tău', ph1='Telefon', hint1='Introdu numărul de telefon',
 s2='Mașina ta', ph2='Număr de înmatriculare', hint2='Introdu cel puțin 3 caractere',
 hintF='Verificăm mașina manual. Descrie-o pe scurt.', phF='Marcă, model, număr',
 s3='Numele tău', ph3='Nume și prenume',
 s4='Trimite cererea', hint4='Se deschide un mesaj gata scris. Doar apeși trimite.',
 okH='Cerere trimisă', okP='Te contactăm în 24 de ore.',
 errName='Te rugăm, nume și prenume.',
 gdpr='Le arătăm clienților doar ce completezi aici. Nimic mai mult.',
 footBG='',
),
'el': dict(
 lead='Αίτηση συμμετοχής. Λιγότερο από ένα λεπτό.',
 h1='0% προμήθεια. Κρατάς ό,τι βγάζεις.',
 p='Οι μεγάλες πλατφόρμες παίρνουν 20–40% από κάθε διαδρομή — στις σύντομες ακόμη περισσότερο. Εμείς τίποτα. Ο πελάτης σε βλέπει, σε καλεί απευθείας και σε πληρώνει.',
 b1='Χωρίς προμήθεια — ούτε τώρα ούτε αργότερα',
 b2='Οι πελάτες σε καλούν απευθείας',
 b3='Σήμα Founder για τους πρώτους — μόνιμο',
 s1='Το τηλέφωνό σου', ph1='Τηλέφωνο', hint1='Δώσε τον αριθμό σου',
 s2='Το αυτοκίνητό σου', ph2='Πινακίδα', hint2='Δώσε τουλάχιστον 3 χαρακτήρες',
 hintF='Ελέγχουμε το όχημα χειροκίνητα. Περίγραψέ το σύντομα.', phF='Μάρκα, μοντέλο, πινακίδα',
 s3='Το όνομά σου', ph3='Όνομα και επώνυμο',
 s4='Αποστολή αίτησης', hint4='Ανοίγει έτοιμο μήνυμα. Πατάς μόνο αποστολή.',
 okH='Η αίτηση στάλθηκε', okP='Θα επικοινωνήσουμε μαζί σου εντός 24 ωρών.',
 errName='Συμπλήρωσε όνομα και επώνυμο.',
 gdpr='Δείχνουμε στους πελάτες μόνο όσα συμπληρώνεις εδώ. Τίποτα άλλο.',
 footBG='',
),
'tr': dict(
 lead='Katılım başvurusu. Bir dakikadan kısa.',
 h1='%0 komisyon. Kazandığın sende kalır.',
 p='Büyük platformlar her yolculuktan %20–40 alır — kısa mesafelerde en çok. Biz hiçbir şey almıyoruz. Müşteri seni görür, doğrudan arar ve sana öder.',
 b1='Komisyon yok — ne şimdi ne sonra',
 b2='Müşteriler seni doğrudan arar',
 b3='İlk sürücülere Founder rozeti — kalıcı',
 s1='Telefonun', ph1='Telefon', hint1='Telefon numaranı gir',
 s2='Aracın', ph2='Plaka', hint2='En az 3 karakter gir',
 hintF='Aracı elle doğruluyoruz. Kısaca tarif et.', phF='Marka, model, plaka',
 s3='Adın', ph3='Ad ve soyad',
 s4='Başvuruyu gönder', hint4='Hazır bir mesaj açılır. Sadece gönder’e basarsın.',
 okH='Başvuru gönderildi', okP='24 saat içinde seninle iletişime geçeceğiz.',
 errName='Lütfen ad ve soyad gir.',
 gdpr='Müşterilere yalnızca burada girdiklerini gösteriyoruz. Başka hiçbir şey.',
 footBG='',
),
'pl': dict(
 lead='Zgłoszenie dołączenia. Poniżej minuty.',
 h1='0% prowizji. Zostaje ci to, co zarobisz.',
 p='Duże platformy biorą 20–40% z każdego kursu — na krótkich najwięcej. My nic. Klient cię widzi, dzwoni bezpośrednio i płaci tobie.',
 b1='Bez prowizji — ani teraz, ani później',
 b2='Klienci dzwonią bezpośrednio do ciebie',
 b3='Odznaka Founder dla pierwszych — na stałe',
 s1='Twój telefon', ph1='Telefon', hint1='Wpisz swój numer telefonu',
 s2='Twój samochód', ph2='Numer rejestracyjny', hint2='Wpisz co najmniej 3 znaki',
 hintF='Pojazd sprawdzamy ręcznie. Opisz go krótko.', phF='Marka, model, numer',
 s3='Twoje imię', ph3='Imię i nazwisko',
 s4='Wyślij zgłoszenie', hint4='Otworzy się gotowa wiadomość. Wystarczy nacisnąć wyślij.',
 okH='Zgłoszenie wysłane', okP='Skontaktujemy się w ciągu 24 godzin.',
 errName='Podaj imię i nazwisko.',
 gdpr='Klientom pokazujemy tylko to, co tu wpiszesz. Nic więcej.',
 footBG='',
),
'nl': dict(
 lead='Aanmelding. Minder dan een minuut.',
 h1='0% commissie. Jij houdt wat je verdient.',
 p='De grote platforms nemen 20–40% van elke rit — op korte ritten het meest. Wij niets. De klant ziet je, belt je direct en betaalt aan jou.',
 b1='Geen commissie — nu niet en later niet',
 b2='Klanten bellen je direct',
 b3='Founder-badge voor de eersten — blijvend',
 s1='Je telefoon', ph1='Telefoon', hint1='Vul je telefoonnummer in',
 s2='Je auto', ph2='Kenteken', hint2='Vul minstens 3 tekens in',
 hintF='We controleren de auto handmatig. Beschrijf hem kort.', phF='Merk, model, kenteken',
 s3='Je naam', ph3='Voor- en achternaam',
 s4='Aanvraag versturen', hint4='Er opent een kant-en-klaar bericht. Je drukt alleen op verzenden.',
 okH='Aanvraag verstuurd', okP='We nemen binnen 24 uur contact op.',
 errName='Vul voor- en achternaam in.',
 gdpr='We tonen klanten alleen wat je hier invult. Niets meer.',
 footBG='',
),
}


def main():
    # проверка: всеки език има всеки ключ
    base = set(T['bg'].keys())
    for l in LANGS:
        assert l in T, f'липсва език {l}'
        miss = base - set(T[l].keys())
        assert not miss, f'{l} без ключове: {miss}'
        if l != 'bg':
            assert not T[l]['footBG'], f'{l} не бива да има текст за БГ регистър'

    def js(v):
        return json.dumps(v, ensure_ascii=False)

    out = []
    out.append('/* Генериран от scripts/gen_join_i18n.py — не редактирай ръчно. */')
    rows = []
    for l in LANGS:
        kv = ','.join(f'{k}:{js(v)}' for k, v in T[l].items())
        rows.append(f' {l}:{{{kv}}}')
    out.append('var JT={\n' + ',\n'.join(rows) + '\n};')
    out.append('var JLANGS=' + js(LANGS) + ';')
    out.append('var JNAMES=' + js(NAMES) + ';')

    out.append(r'''
/* Езикът се познава от браузъра, с ръчно превключване.  Изборът се
   помни в същия ключ като на клиентската страница, за да е един и
   същ език и на двете места.                                      */
var jlang=(function(){
  try{
    var s=localStorage.getItem('fishtaxi-lang');
    if(s&&JT[s])return s;
  }catch(e){}
  var n=(navigator.language||'en').slice(0,2).toLowerCase();
  return JT[n]?n:'en';
})();
function jt(){ return JT[jlang]||JT.en; }
function jSetT(id,v){ var e=document.getElementById(id); if(e&&v!=null)e.textContent=v; }
function jSetPH(id,v){ var e=document.getElementById(id); if(e&&v!=null)e.placeholder=v; }
function applyJoinLang(l){
  if(l){ jlang=l; try{localStorage.setItem('fishtaxi-lang',l);}catch(e){} }
  var t=jt();
  document.documentElement.lang=jlang;
  jSetT('j-lead',t.lead); jSetT('j-h1',t.h1); jSetT('j-p',t.p);
  jSetT('j-b1',t.b1); jSetT('j-b2',t.b2); jSetT('j-b3',t.b3);
  jSetT('j-s1',t.s1); jSetPH('phone',t.ph1); jSetT('phoneHint',t.hint1);
  jSetT('j-s2',t.s2); jSetPH('q',t.ph2); jSetT('hint',t.hint2);
  jSetT('j-s2f',t.s2); jSetT('j-hintF',t.hintF); jSetPH('carManual',t.phF);
  jSetT('j-s3',t.s3); jSetPH('name',t.ph3);
  jSetT('j-s4',t.s4); jSetT('j-hint4',t.hint4);
  jSetT('j-okH',t.okH); jSetT('j-okP',t.okP);
  jSetT('j-gdpr',t.gdpr);
  /* Българският регистър се показва само на български. */
  var fb=document.getElementById('j-footBG');
  if(fb){ fb.textContent=t.footBG||''; fb.style.display=t.footBG?'':'none'; }
  var sel=document.getElementById('j-lang');
  if(sel&&sel.value!==jlang)sel.value=jlang;
}
document.addEventListener('DOMContentLoaded',function(){
  var sel=document.getElementById('j-lang');
  if(sel){
    JLANGS.forEach(function(l){
      var o=document.createElement('option');
      o.value=l; o.textContent=JNAMES[l]||l; sel.appendChild(o);
    });
    sel.value=jlang;
    sel.addEventListener('change',function(){ applyJoinLang(sel.value); });
  }
  applyJoinLang();
});''')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
