# fish.taxi — италиански, испански и френски + места на латиница (17.11.2026)
# 1) lib/app-i18n.js (речници it/es/fr) се пише от patch_i18n_dict.py, пуснат преди този
# 2) app-core: зарежда езиците, разпознава езика на телефона, F.tx / F.lat / F.loc / F.dc
# 3) мишената (обратно геокодиране) и адресите от Photon: lang=en + транслитерация, ако езикът не е bg
# 4) известните места (НДК, Летище...) с преводи; менюто показва всички езици
# Идемпотентен: всеки файл се пропуска, ако вече е пачнат.
import io
def patch(fn, pairs, done):
    t = io.open(fn, encoding='utf-8').read()
    if done in t:
        print('already', fn); return
    for old, new, *n in pairs:
        c = t.count(old)
        want = n[0] if n else 1
        assert c == want, f'{fn}: expected {want}x, found {c}x: {old[:70]}'
        t = t.replace(old, new)
    io.open(fn, 'w', encoding='utf-8', newline='\n').write(t)
    print('ok', fn)

# ---------- app-core.js ----------
patch('lib/app-core.js', [
 ("var LN={bg:'Български'",
  "/* допълнителни езици от lib/app-i18n.js (зарежда се преди този файл) */\n"
  "var X={},I=window.FT_I18N||{};for(var il in I){S[il]=I[il].S;X[il]=I[il].X||{};}\n"
  "F.LANGS=Object.keys(S);\n"
  "var LN={bg:'Български'"),
 ("if(!S[F.lang])F.lang=/^bg/i.test(navigator.language||'bg')?'bg':'en';",
  "if(!S[F.lang]){var nl=String(navigator.language||'bg').slice(0,2).toLowerCase();F.lang=S[nl]?nl:'en';}"),
 ("F.setLang=function(l){",
  "/* вграден текст: български или английски; за другите езици — превод на английския от app-i18n.js */\n"
  "F.tx=function(bg,en){if(F.lang==='bg')return bg;var d=X[F.lang];return (d&&d[en])||en;};\n"
  "F.dc=function(){return F.lang==='en'?'.':',';};\n"
  "/* кирилица → латиница (официалната българска транслитерация); само ако езикът не е български */\n"
  "var TL={'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sht','ъ':'a','ь':'y','ю':'yu','я':'ya','ё':'yo','э':'e','ы':'y'};\n"
  "F.lat=function(s){s=String(s==null?'':s).replace(/ия(?![а-яё])/g,'ia').replace(/ИЯ(?![А-ЯЁ])/g,'IA').replace(/Ия(?![а-яё])/g,'Ia');\n"
  " return s.replace(/[А-ЯЁа-яё]/g,function(c,i){var lo=c.toLowerCase(),r=TL[lo];if(r===undefined)return c;if(c===lo)return r;\n"
  "  var nx=s.charAt(i+1);return (nx&&nx!==nx.toLowerCase())?r.toUpperCase():r.charAt(0).toUpperCase()+r.slice(1);});};\n"
  "F.loc=function(s){return (F.lang!=='bg'&&/[\\u0400-\\u04FF]/.test(s||''))?F.lat(s):(s||'');};\n"
  "F.geoLang=function(){return F.lang==='bg'?'':'&lang=en';};\n"
  "F.setLang=function(l){"),
 (".replace('.',F.lang==='bg'?',':'.')+' '+F.t('km')", ".replace('.',F.dc())+' '+F.t('km')"),
 ("F.toast('Няма връзка. Презареди страницата.')", "F.toast(F.tx('Няма връзка. Презареди страницата.','No connection. Reload the page.'))"),
], 'F.tx=function')

# ---------- app-route.js ----------
patch('lib/app-route.js', [
 ("function T(bg,en){return F.lang==='bg'?bg:en;}", "var T=F.tx;"),
 ("function eur(p){return p.toFixed(2).replace('.',F.lang==='bg'?',':'.')+' €';}",
  "function eur(p){return p.toFixed(2).replace('.',F.dc())+' €';}"),
 ("fetch('https://photon.komoot.io/reverse?lat='+p.lat+'&lon='+p.lng+'&limit=1')",
  "fetch('https://photon.komoot.io/reverse?lat='+p.lat+'&lon='+p.lng+'&limit=1'+F.geoLang())"),
 ("if(!name)return;R.to.label=name+(q.name&&st?', '+st:'')+(q.city&&q.city!==name?', '+q.city:'');render();",
  "if(!name)return;R.to.label=F.loc(name+(q.name&&st?', '+st:'')+(q.city&&q.city!==name?', '+q.city:''));render();"),
], 'var T=F.tx;')

# ---------- app-order.js ----------
patch('lib/app-order.js', [
 ("function L(bg,en){return F.lang==='bg'?bg:en;}", "var L=F.tx;"),
 ("p.toFixed(2).replace('.',F.lang==='bg'?',':'.')", "p.toFixed(2).replace('.',F.dc())"),
 ("['НДК','Национален дворец на културата, София',42.6857,23.3190,'ндк ndk дворец palace culture'],",
  "['НДК','Национален дворец на културата, София',42.6857,23.3190,'ндк ndk дворец palace culture','NDK','National Palace of Culture, Sofia'],"),
 ("['Летище София','Терминал 1 и 2, София',42.6952,23.4064,'летище аерогара airport sofia терминал'],",
  "['Летище София','Терминал 1 и 2, София',42.6952,23.4064,'летище аерогара airport sofia терминал','Sofia Airport','Terminal 1 and 2, Sofia'],"),
 ("['Централна гара','Гара София',42.7122,23.3210,'гара централна railway station'],",
  "['Централна гара','Гара София',42.7122,23.3210,'гара централна railway station','Central Railway Station','Sofia'],"),
 ("['Автогара Сердика','Централна автогара, София',42.7117,23.3209,'автогара сердика bus station'],",
  "['Автогара Сердика','Централна автогара, София',42.7117,23.3209,'автогара сердика bus station','Serdika Bus Station','Central bus station, Sofia'],"),
 ("['Александър Невски','Храм-паметник, София',42.6957,23.3327,'александър невски катедрала cathedral'],",
  "['Александър Невски','Храм-паметник, София',42.6957,23.3327,'александър невски катедрала cathedral','Alexander Nevsky Cathedral','Sofia'],"),
 ("['Парадайс център','бул. Черни връх, София',42.6573,23.3153,'парадайс paradise mall'],",
  "['Парадайс център','бул. Черни връх, София',42.6573,23.3153,'парадайс paradise mall','Paradise Center','Cherni Vrah Blvd, Sofia'],"),
 ("['Национален стадион Васил Левски','София',42.6853,23.3347,'стадион левски stadium']];",
  "['Национален стадион Васил Левски','София',42.6853,23.3347,'стадион левски stadium','Vasil Levski National Stadium','Sofia']];"),
 ("return {lat:c[1],lng:c[0],name:name,label:name+(p.city&&p.city!==name?', '+p.city:''),sub:[p.name?st:'',p.city,p.country].filter(Boolean).join(', ')};",
  "return {lat:c[1],lng:c[0],name:F.loc(name),label:F.loc(name+(p.city&&p.city!==name?', '+p.city:'')),sub:F.loc([p.name?st:'',p.city,p.country].filter(Boolean).join(', '))};"),
 ("return PLACES.map(function(p){return {lat:p[2],lng:p[3],name:p[0],label:p[0],sub:p[1],d:dkm(r.lat,r.lng,p[2],p[3]),h:(p[0]+' '+p[4]).toLowerCase()};})",
  "return PLACES.map(function(p){var nm=L(p[0],p[5]);return {lat:p[2],lng:p[3],name:nm,label:nm,sub:L(p[1],p[6]),d:dkm(r.lat,r.lng,p[2],p[3]),h:(p[0]+' '+p[4]+' '+p[5]+' '+nm).toLowerCase()};})"),
 ("base='https://photon.komoot.io/api/?q='+encodeURIComponent(q)+'&lat='+r.lat+'&lon='+r.lng;",
  "base='https://photon.komoot.io/api/?q='+encodeURIComponent(q)+'&lat='+r.lat+'&lon='+r.lng+F.geoLang();"),
], 'var L=F.tx;')

# ---------- app-ui.js ----------
patch('lib/app-ui.js', [
 ("function eur(n){return n.toFixed(2).replace('.',F.lang==='bg'?',':'.')+' €';}",
  "function eur(n){return n.toFixed(2).replace('.',F.dc())+' €';}"),
 ("function qrGroup(d){var bg=F.lang==='bg';return ", "function qrGroup(d){return "),
 ("(bg?'QR за контактите.<br>Докосни за цял екран':'Contact QR.<br>Tap for full screen')",
  "F.tx('QR за контактите.<br>Докосни за цял екран','Contact QR.<br>Tap for full screen')"),
 ("(F.lang==='bg'?'Докосни за затваряне':'Tap to close')", "F.tx('Докосни за затваряне','Tap to close')"),
 ("return GEN[g][F.lang==='bg'?0:1];", "return F.tx(GEN[g][0],GEN[g][1]);"),
 ("['bg','en'].map(function(l){return '<button class=\"chip\" data-l=\"'",
  "F.LANGS.map(function(l){return '<button class=\"chip\" data-l=\"'"),
 ("<a href=\"privacy.html\" style=\"color:inherit\">'+(F.lang==='bg'?'Поверителност':'Privacy')+'</a>",
  "<a href=\"privacy.html'+(F.lang==='bg'?'':'#en')+'\" style=\"color:inherit\">'+F.tx('Поверителност','Privacy')+'</a>"),
 ("function texts(){\n",
  "function texts(){\n"
  "  document.title='fish.taxi — '+F.tx('такси директно от шофьора','taxi straight from the driver');\n"
  "  $('map').setAttribute('aria-label',F.tx('Карта','Map'));$('locate').setAttribute('aria-label',t('locOk'));\n"
  "  [].forEach.call(document.querySelectorAll('.pclose'),function(b){b.setAttribute('aria-label',F.tx('Затвори','Close'));});\n"),
], 'F.LANGS.map')

# ---------- app-theme.js ----------
patch('lib/app-theme.js', [
 ("function T(bg,en){return F.lang==='bg'?bg:en;}", "function T(bg,en){return F.tx(bg,en);}"),
], 'return F.tx(bg,en)')

# ---------- app-fs.js ----------
patch('lib/app-fs.js', [
 ("function bg(){return de.lang!=='en';}",
  "function tx(b,e){return (window.FT&&FT.tx)?FT.tx(b,e):(de.lang==='bg'?b:e);}"),
 ("function label(){return (bg()?'Цял екран: ':'Full screen: ')+(want()?(bg()?'вкл.':'on'):(bg()?'изкл.':'off'));}",
  "function label(){return tx('Цял екран: ','Full screen: ')+(want()?tx('вкл.','on'):tx('изкл.','off'));}"),
 ("(bg()?'скрива лентата горе':'hides the top bar')", "tx('скрива лентата горе','hides the top bar')"),
], 'function tx(b,e)')

# ---------- страници: app-i18n.js преди app-core.js, нови версии против кеша ----------
patch('index.html', [
 ('<script src="lib/app-core.js?v=6"></script>', '<script src="lib/app-i18n.js?v=1"></script>\n<script src="lib/app-core.js?v=7"></script>'),
 ('lib/app-ui.js?v=10', 'lib/app-ui.js?v=11'), ('lib/app-order.js?v=5', 'lib/app-order.js?v=6'),
 ('lib/app-route.js?v=5', 'lib/app-route.js?v=6'), ('lib/app-theme.js?v=1', 'lib/app-theme.js?v=2'), ('lib/app-fs.js?v=5', 'lib/app-fs.js?v=6'),
], 'lib/app-i18n.js')
patch('app.html', [
 ('<script src="lib/app-core.js?v=1"></script>', '<script src="lib/app-i18n.js?v=1"></script>\n<script src="lib/app-core.js?v=7"></script>'),
 ('lib/app-ui.js?v=1"', 'lib/app-ui.js?v=11"'), ('lib/app-order.js?v=1"', 'lib/app-order.js?v=6"'),
], 'lib/app-i18n.js')
