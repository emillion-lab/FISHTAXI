# fish.taxi — речници it/es/fr → lib/app-i18n.js (17.11.2026). Пуска се преди patch_i18n_code.py.
# Идемпотентен: винаги пише файла наново от речниците по-долу.
import io, json


S = {}
S['it'] = dict(
 nearT='Autisti nelle vicinanze', free='autisti liberi nelle vicinanze', free1='autista libero nelle vicinanze', none='Nessun autista nelle vicinanze', nearN='autisti nelle vicinanze', near1='autista nelle vicinanze',
 offHint='Gli autisti non devono per forza essere online: puoi ordinare anche da un autista offline e accordarti direttamente.',
 online='online', offline='offline', updated='aggiornato', now='ora', ago='', sec='s fa', min='min', km='km',
 slide='Scorri per un taxi', fOn='Solo online', fEn='Inglese', fChild='Seggiolino', fCard='Carta', fPet='Animali', fEv='Elettrica', fBig='6+ posti',
 call='Chiama', details='Foto e dettagli', orderAt='Ordina con', other='In altre città', noMatch='Nessun autista con questi filtri. Togline uno.',
 car='Auto', plate='Targa', seats='Posti', pay='Pagamento', tariff='Tariffa', start='partenza', day='giorno', night='notte', music='Musica', langs='Lingue', pets='Animali', child='Seggiolino per bambini', airport='Aeroporto', longd='Viaggi lunghi', nightw='Di notte', wheel='Sedia a rotelle', areas='Zone', phone='Telefono',
 yes='Sì', no='No', ask='Su richiesta', cash='Contanti', terminal='Carta (POS)', revolut='Revolut', onreq='Su richiesta', anyMusic='A tua scelta', noMusic='Niente musica',
 xEv='Elettrica', xAc='Aria condizionata', xUsb='Caricatore USB', xStream='Musica dal tuo telefono', xRoof='Tetto panoramico', xLeg='Spazio per le gambe', xTint='Vetri oscurati', xNos='Non fumatore', xQuiet='Viaggio silenzioso su richiesta', xVer='Autista verificato',
 share='Condividi', copied='Link copiato.',
 oTitle='Ordina con', pickup='Ritiro', locOk='La mia posizione', locWait='Ti sto cercando…', locNo='Niente GPS. Invia l’indirizzo in chat.', retry='Riprova', when='Quando', wNow='Ora', wLater='Più tardi', pax='Passeggeri', wishes='Preferenze',
 pQuiet='Silenzio', pTalk='Chiacchiere', pCalm='Guida tranquilla', pMusic='Musica', pBag='Bagaglio grande', dest='Destinazione (facoltativa)', destPh='Indirizzo o luogo',
 sms='Invia SMS', wa='WhatsApp', viber='Viber', vCopied='Ordine copiato. Incollalo nella chat di Viber.', notOnline='Non è online, ma puoi ordinare e accordarti direttamente: risponde appena lo vede.', noDrivers='Nessun autista nelle vicinanze.',
 menu='Menu', join='Diventa autista', profil='Il mio profilo', profilS='per autisti', classic='Vecchio sito', lang='Lingua', about='Contatto diretto con l’autista, senza commissioni.', osm='Mappa: © OpenStreetMap', locDenied='Nessun accesso alla tua posizione.')

S['es'] = dict(
 nearT='Conductores cerca', free='conductores libres cerca', free1='conductor libre cerca', none='No hay conductores cerca', nearN='conductores cerca', near1='conductor cerca',
 offHint='Los conductores no tienen que estar en línea: también puedes pedir a un conductor desconectado y acordarlo directamente.',
 online='en línea', offline='desconectado', updated='actualizado', now='ahora', ago='hace', sec='s', min='min', km='km',
 slide='Desliza para pedir taxi', fOn='Solo en línea', fEn='Inglés', fChild='Silla infantil', fCard='Tarjeta', fPet='Mascotas', fEv='Eléctrico', fBig='6+ plazas',
 call='Llamar', details='Fotos y detalles', orderAt='Pedir a', other='En otras ciudades', noMatch='Ningún conductor con estos filtros. Quita alguno.',
 car='Coche', plate='Matrícula', seats='Plazas', pay='Pago', tariff='Tarifa', start='inicio', day='día', night='noche', music='Música', langs='Idiomas', pets='Mascotas', child='Silla infantil', airport='Aeropuerto', longd='Viajes largos', nightw='De noche', wheel='Silla de ruedas', areas='Zonas', phone='Teléfono',
 yes='Sí', no='No', ask='A consultar', cash='Efectivo', terminal='Tarjeta (TPV)', revolut='Revolut', onreq='A consultar', anyMusic='A tu elección', noMusic='Sin música',
 xEv='Eléctrico', xAc='Aire acondicionado', xUsb='Cargador USB', xStream='Música desde tu móvil', xRoof='Techo panorámico', xLeg='Espacio para las piernas', xTint='Lunas tintadas', xNos='No fumador', xQuiet='Viaje en silencio si lo pides', xVer='Conductor verificado',
 share='Compartir', copied='Enlace copiado.',
 oTitle='Pedir a', pickup='Recogida', locOk='Mi ubicación', locWait='Buscando dónde estás…', locNo='Sin GPS. Envía la dirección en el chat.', retry='Reintentar', when='Cuándo', wNow='Ahora', wLater='Más tarde', pax='Pasajeros', wishes='Preferencias',
 pQuiet='Silencio', pTalk='Charla', pCalm='Conducción tranquila', pMusic='Música', pBag='Equipaje grande', dest='Destino (opcional)', destPh='Dirección o lugar',
 sms='Enviar SMS', wa='WhatsApp', viber='Viber', vCopied='Pedido copiado. Pégalo en el chat de Viber.', notOnline='No está en línea, pero puedes pedir y acordarlo directamente: responde cuando lo vea.', noDrivers='No hay conductores cerca.',
 menu='Menú', join='Hazte conductor', profil='Mi perfil', profilS='para conductores', classic='Web antigua', lang='Idioma', about='Contacto directo con el conductor, sin comisión.', osm='Mapa: © OpenStreetMap', locDenied='Sin acceso a tu ubicación.')

S['fr'] = dict(
 nearT='Chauffeurs à proximité', free='chauffeurs libres à proximité', free1='chauffeur libre à proximité', none='Aucun chauffeur à proximité', nearN='chauffeurs à proximité', near1='chauffeur à proximité',
 offHint='Les chauffeurs ne sont pas obligés d’être en ligne : vous pouvez aussi commander auprès d’un chauffeur hors ligne et vous arranger directement.',
 online='en ligne', offline='hors ligne', updated='mis à jour', now='à l’instant', ago='il y a', sec='s', min='min', km='km',
 slide='Glissez pour un taxi', fOn='En ligne seulement', fEn='Anglais', fChild='Siège enfant', fCard='Carte', fPet='Animaux', fEv='Électrique', fBig='6+ places',
 call='Appeler', details='Photos et détails', orderAt='Commander à', other='Dans d’autres villes', noMatch='Aucun chauffeur avec ces filtres. Retirez-en un.',
 car='Voiture', plate='Plaque', seats='Places', pay='Paiement', tariff='Tarif', start='prise en charge', day='jour', night='nuit', music='Musique', langs='Langues', pets='Animaux', child='Siège enfant', airport='Aéroport', longd='Longs trajets', nightw='La nuit', wheel='Fauteuil roulant', areas='Zones', phone='Téléphone',
 yes='Oui', no='Non', ask='Sur demande', cash='Espèces', terminal='Carte (TPE)', revolut='Revolut', onreq='Sur demande', anyMusic='À votre choix', noMusic='Sans musique',
 xEv='Électrique', xAc='Climatisation', xUsb='Chargeur USB', xStream='Musique depuis votre téléphone', xRoof='Toit panoramique', xLeg='Espace pour les jambes', xTint='Vitres teintées', xNos='Non-fumeur', xQuiet='Trajet silencieux sur demande', xVer='Chauffeur vérifié',
 share='Partager', copied='Lien copié.',
 oTitle='Commande à', pickup='Prise en charge', locOk='Ma position', locWait='Recherche de votre position…', locNo='Pas de GPS. Envoyez l’adresse dans le chat.', retry='Réessayer', when='Quand', wNow='Maintenant', wLater='Plus tard', pax='Passagers', wishes='Préférences',
 pQuiet='Silence', pTalk='Discussion', pCalm='Conduite calme', pMusic='Musique', pBag='Gros bagages', dest='Destination (facultatif)', destPh='Adresse ou lieu',
 sms='Envoyer un SMS', wa='WhatsApp', viber='Viber', vCopied='Commande copiée. Collez-la dans le chat Viber.', notOnline='Pas en ligne, mais vous pouvez commander et vous arranger directement : il répond dès qu’il le voit.', noDrivers='Aucun chauffeur à proximité.',
 menu='Menu', join='Devenir chauffeur', profil='Mon profil', profilS='pour chauffeurs', classic='Ancien site', lang='Langue', about='Contact direct avec le chauffeur, sans commission.', osm='Carte : © OpenStreetMap', locDenied='Pas d’accès à votre position.')

# Inline texts: English text -> [it, es, fr]
X = {
 'Finding routes…': ['Cerco percorsi…', 'Buscando rutas…', 'Recherche d’itinéraires…'],
 'No route to this point. Try a bit closer to a road.': ['Nessun percorso fino a questo punto. Prova un po’ più vicino a una strada.', 'No hay ruta hasta este punto. Prueba un poco más cerca de una carretera.', 'Aucun itinéraire jusqu’à ce point. Essayez un peu plus près d’une route.'],
 '⚡ Fastest': ['⚡ Più veloce', '⚡ Más rápida', '⚡ Le plus rapide'],
 '📏 Shortest': ['📏 Più breve', '📏 Más corta', '📏 Le plus court'],
 '📏 and shortest': ['📏 e più breve', '📏 y más corta', '📏 et le plus court'],
 'Other route': ['Altro percorso', 'Otra ruta', 'Autre itinéraire'],
 'Close': ['Chiudi', 'Cerrar', 'Fermer'],
 'Where to': ['Destinazione', 'Destino', 'Destination'],
 'from the centre (no GPS)': ['dal centro (niente GPS)', 'desde el centro (sin GPS)', 'depuis le centre (pas de GPS)'],
 'Order to here': ['Ordina fin qui', 'Pedir hasta aquí', 'Commander jusqu’ici'],
 'No driver nearby.': ['Nessun autista nelle vicinanze.', 'No hay conductores cerca.', 'Aucun chauffeur à proximité.'],
 'Routing server unavailable — straight-line estimate.': ['Server dei percorsi non disponibile: stima in linea d’aria.', 'Servidor de rutas no disponible: estimación en línea recta.', 'Serveur d’itinéraires indisponible : estimation à vol d’oiseau.'],
 'Times assume normal traffic, not live.': ['Tempi con traffico normale, non in tempo reale.', 'Tiempos con tráfico normal, no en directo.', 'Temps pour un trafic normal, pas en direct.'],
 'Choose a driver': ['Scegli un autista', 'Elige un conductor', 'Choisissez un chauffeur'],
 'Online and offline — agree directly': ['Online e offline: accordatevi direttamente', 'En línea y desconectados: acuérdalo directamente', 'En ligne et hors ligne : arrangez-vous directement'],
 'Back': ['Indietro', 'Atrás', 'Retour'],
 'Choose a driver to': ['Scegli un autista per', 'Elige un conductor hasta', 'Choisissez un chauffeur pour'],
 'min away': ['min da te', 'min de distancia', 'min de vous'],
 'online': ['online', 'en línea', 'en ligne'],
 'offline': ['offline', 'desconectado', 'hors ligne'],
 'seats': ['posti', 'plazas', 'places'],
 "Price uses the driver's tariff for the chosen route.": ['Il prezzo segue la tariffa dell’autista per il percorso scelto.', 'El precio sigue la tarifa del conductor para la ruta elegida.', 'Le prix suit le tarif du chauffeur pour l’itinéraire choisi.'],
 'Press and hold on the map to choose where to': ['Tieni premuto sulla mappa per scegliere dove andare', 'Mantén pulsado el mapa para elegir adónde ir', 'Appuyez longuement sur la carte pour choisir où aller'],
 '📍 Use my location': ['📍 Usa la mia posizione', '📍 Usar mi ubicación', '📍 Utiliser ma position'],
 'My location or another address': ['La mia posizione o un altro indirizzo', 'Mi ubicación u otra dirección', 'Ma position ou une autre adresse'],
 'Passenger — name and phone (optional)': ['Passeggero: nome e telefono (facoltativo)', 'Pasajero: nombre y teléfono (opcional)', 'Passager : nom et téléphone (facultatif)'],
 'Day mode — tap for night': ['Modalità giorno: tocca per la notte', 'Modo día: toca para modo noche', 'Mode jour : touchez pour la nuit'],
 'Night mode — tap for day': ['Modalità notte: tocca per il giorno', 'Modo noche: toca para modo día', 'Mode nuit : touchez pour le jour'],
 '☀️ Day mode · tap the logo for night': ['☀️ Modalità giorno · tocca il logo per la notte', '☀️ Modo día · toca el logo para modo noche', '☀️ Mode jour · touchez le logo pour la nuit'],
 '🌙 Night mode · tap the logo for day': ['🌙 Modalità notte · tocca il logo per il giorno', '🌙 Modo noche · toca el logo para modo día', '🌙 Mode nuit · touchez le logo pour le jour'],
 'Full screen: ': ['Schermo intero: ', 'Pantalla completa: ', 'Plein écran : '],
 'on': ['attivo', 'activada', 'activé'],
 'off': ['disattivo', 'desactivada', 'désactivé'],
 'hides the top bar': ['nasconde la barra in alto', 'oculta la barra superior', 'masque la barre du haut'],
 'Contact QR.<br>Tap for full screen': ['QR del contatto.<br>Tocca per schermo intero', 'QR de contacto.<br>Toca para pantalla completa', 'QR du contact.<br>Touchez pour le plein écran'],
 'Tap to close': ['Tocca per chiudere', 'Toca para cerrar', 'Touchez pour fermer'],
 'Privacy': ['Privacy', 'Privacidad', 'Confidentialité'],
 'Classical': ['Classica', 'Clásica', 'Classique'],
 'Electronic': ['Elettronica', 'Electrónica', 'Électronique'],
 'No connection. Reload the page.': ['Nessuna connessione. Ricarica la pagina.', 'Sin conexión. Recarga la página.', 'Pas de connexion. Rechargez la page.'],
 'taxi straight from the driver': ['taxi direttamente dall’autista', 'taxi directo del conductor', 'taxi en direct avec le chauffeur'],
 'Map': ['Mappa', 'Mapa', 'Carte'],
 # places
 'National Palace of Culture, Sofia': ['Palazzo nazionale della cultura, Sofia', 'Palacio Nacional de la Cultura, Sofía', 'Palais national de la culture, Sofia'],
 'Sofia Airport': ['Aeroporto di Sofia', 'Aeropuerto de Sofía', 'Aéroport de Sofia'],
 'Terminal 1 and 2, Sofia': ['Terminal 1 e 2, Sofia', 'Terminales 1 y 2, Sofía', 'Terminaux 1 et 2, Sofia'],
 'Central Railway Station': ['Stazione centrale', 'Estación central de tren', 'Gare centrale'],
 'Sofia': ['Sofia', 'Sofía', 'Sofia'],
 'Serdika Bus Station': ['Autostazione Serdika', 'Estación de autobuses Serdika', 'Gare routière Serdika'],
 'Central bus station, Sofia': ['Autostazione centrale, Sofia', 'Estación central de autobuses, Sofía', 'Gare routière centrale, Sofia'],
 'Alexander Nevsky Cathedral': ['Cattedrale Alexander Nevsky', 'Catedral de Alejandro Nevski', 'Cathédrale Alexandre-Nevski'],
 'Cherni Vrah Blvd, Sofia': ['Viale Cherni Vrah, Sofia', 'Bulevar Cherni Vrah, Sofía', 'Boulevard Cherni Vrah, Sofia'],
 'Vasil Levski National Stadium': ['Stadio nazionale Vasil Levski', 'Estadio Nacional Vasil Levski', 'Stade national Vasil-Levski'],
}

out = {}
for i, l in enumerate(['it', 'es', 'fr']):
    out[l] = {'S': S[l], 'X': {k: v[i] for k, v in X.items()}}

js = ('/* fish.taxi — преводи на италиански, испански и френски.\n'
      ' * S: същите ключове като в app-core.js; X: вградени текстове по английския им вариант.\n'
      ' * Зарежда се ПРЕДИ app-core.js. Нов език = нов ключ тук. */\n'
      'window.FT_I18N=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
io.open('lib/app-i18n.js', 'w', encoding='utf-8', newline='\n').write(js)
print('lib/app-i18n.js', len(js.encode()), 'bytes', {l: len(S[l]) for l in S})
