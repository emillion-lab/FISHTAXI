/* fish.taxi v3 — ядро: настройки, текстове, данни, живи позиции. */
var FT=(function(){
"use strict";
var F={WORKER:'https://mvr-proxy.mihov-emil.workers.dev',C:[42.6977,23.3219],NEAR_KM:60,D:[],me:null,filters:{},sel:null};
var $=F.$=function(id){return document.getElementById(id);};

/* ---------- език ---------- */
var S={
bg:{free:'свободни наблизо',free1:'свободен наблизо',none:'Няма шофьори наблизо',nearN:'шофьори наблизо',near1:'шофьор наблизо',offHint:'Шофьорите не са длъжни да са онлайн — можеш да поръчаш и при офлайн шофьор, като се разберете директно.',online:'онлайн',offline:'офлайн',updated:'обновено',now:'сега',ago:'преди',sec:'с',min:'мин',km:'км',
 slide:'Плъзни за такси',fOn:'Само онлайн',fEn:'English',fChild:'Детско столче',fCard:'Карта',fPet:'Любимци',fEv:'Електрическа',fBig:'6+ места',
 call:'Обади се',details:'Снимки и подробности',orderAt:'Поръчай при',other:'В други градове',noMatch:'Няма шофьор с тези филтри. Махни някой филтър.',
 car:'Кола',plate:'Номер',seats:'Места',pay:'Плащане',tariff:'Тарифа',start:'начална',day:'ден',night:'нощ',music:'Музика',langs:'Езици',pets:'Домашни любимци',child:'Детско столче',airport:'Летище',longd:'Дълги курсове',nightw:'Нощем',wheel:'Инвалидна количка',areas:'Райони',phone:'Телефон',
 yes:'Да',no:'Не',ask:'По договаряне',cash:'В брой',terminal:'Карта (ПОС)',revolut:'Revolut',onreq:'По заявка',anyMusic:'По избор',noMusic:'Без музика',
 xEv:'Електрическа',xAc:'Климатик',xUsb:'Зарядно USB',xStream:'Музика от телефона',xRoof:'Панорамен покрив',xLeg:'Място за краката',xTint:'Затъмнени стъкла',xNos:'Непушач',xQuiet:'Тишина при желание',xVer:'Проверен шофьор',
 share:'Сподели',copied:'Връзката е копирана.',
 oTitle:'Поръчка при',pickup:'Вземане',locOk:'Моето местоположение',locWait:'Търся къде си…',locNo:'Без GPS. Ще пратиш адреса в чата.',retry:'Опитай пак',when:'Кога',wNow:'Сега',wLater:'По-късно',pax:'Пътници',wishes:'Желания',
 pQuiet:'Тишина',pTalk:'Разговор',pCalm:'Спокойно каране',pMusic:'Музика',pBag:'Голям багаж',dest:'Докъде (по желание)',destPh:'Адрес или място',
 sms:'Изпрати SMS',wa:'WhatsApp',viber:'Viber',vCopied:'Поръчката е копирана. Постави я в чата във Viber.',notOnline:'Не е онлайн, но можеш да поръчаш и се разберете директно — отговаря, когато види.',noDrivers:'Няма шофьори наблизо.',
 menu:'Меню',join:'Стани шофьор',profil:'Моят профил',profilS:'за шофьори',classic:'Старият сайт',lang:'Език',about:'Директна връзка с шофьора, без комисиона.',osm:'Карта: © OpenStreetMap',locDenied:'Няма достъп до местоположението.'},
en:{free:'drivers free nearby',free1:'driver free nearby',none:'No drivers nearby',nearN:'drivers nearby',near1:'driver nearby',offHint:'Drivers are not required to be online — you can still order from an offline driver and agree directly.',online:'online',offline:'offline',updated:'updated',now:'now',ago:'',sec:'s ago',min:'min',km:'km',
 slide:'Slide for a taxi',fOn:'Online only',fEn:'English',fChild:'Child seat',fCard:'Card',fPet:'Pets',fEv:'Electric',fBig:'6+ seats',
 call:'Call',details:'Photos & details',orderAt:'Order with',other:'In other cities',noMatch:'No driver matches these filters. Remove one.',
 car:'Car',plate:'Plate',seats:'Seats',pay:'Payment',tariff:'Tariff',start:'start',day:'day',night:'night',music:'Music',langs:'Languages',pets:'Pets',child:'Child seat',airport:'Airport',longd:'Long trips',nightw:'At night',wheel:'Wheelchair',areas:'Areas',phone:'Phone',
 yes:'Yes',no:'No',ask:'On request',cash:'Cash',terminal:'Card (POS)',revolut:'Revolut',onreq:'On request',anyMusic:'Your choice',noMusic:'No music',
 xEv:'Electric',xAc:'Air conditioning',xUsb:'USB charger',xStream:'Music from your phone',xRoof:'Panoramic roof',xLeg:'Legroom',xTint:'Tinted windows',xNos:'Non-smoker',xQuiet:'Quiet ride on request',xVer:'Verified driver',
 share:'Share',copied:'Link copied.',
 oTitle:'Order with',pickup:'Pickup',locOk:'My location',locWait:'Finding you…',locNo:'No GPS. Send the address in the chat.',retry:'Try again',when:'When',wNow:'Now',wLater:'Later',pax:'Passengers',wishes:'Wishes',
 pQuiet:'Silence',pTalk:'Chat',pCalm:'Calm driving',pMusic:'Music',pBag:'Large luggage',dest:'Where to (optional)',destPh:'Address or place',
 sms:'Send SMS',wa:'WhatsApp',viber:'Viber',vCopied:'Order copied. Paste it in the Viber chat.',notOnline:'Not online, but you can still order and agree directly — replies when they see it.',noDrivers:'No drivers nearby.',
 menu:'Menu',join:'Become a driver',profil:'My profile',profilS:'for drivers',classic:'Old site',lang:'Language',about:'Direct contact with the driver, no commission.',osm:'Map: © OpenStreetMap',locDenied:'No access to your location.'}
};
var LN={bg:'Български',en:'English',ru:'Русский',de:'Deutsch',fr:'Français',tr:'Türkçe',it:'Italiano',es:'Español',cs:'Čeština',ar:'العربية',zh:'中文'};
F.LN=LN;
F.dur=function(min){min=Math.round(min);var bg=F.lang==='bg';if(min<60)return min+' '+(bg?'мин':'min');var h=Math.floor(min/60),m=min%60;return h+' '+(bg?'ч':'h')+(m?' '+m+' '+(bg?'мин':'min'):'');};
try{F.lang=localStorage.getItem('ft_lang');}catch(e){}
if(!S[F.lang])F.lang=/^bg/i.test(navigator.language||'bg')?'bg':'en';
F.t=function(k){return (S[F.lang]&&S[F.lang][k]!==undefined)?S[F.lang][k]:(S.en[k]||k);};
F.setLang=function(l){F.lang=l;try{localStorage.setItem('ft_lang',l);}catch(e){}document.documentElement.lang=l;};

/* Биографии на български (в данните са на английски). */
var BIO={
 1:'Непушач. IT специалист. Живял съм в чужбина. Без животни, храна и напитки в колата. С удоволствие говоря или мълча. Кажете, ако искате определен маршрут или не се чувствате добре.',
 2:'Непушач. IT специалист. Спокойно, плавно каране. Музика по желание на клиента — ваш избор през YouTube. Багажник 540 л. Качвам малки домашни любимци.',
 3:'VIP трансфери по Френската Ривиера през лятото (Ница, Кан, Сен Тропе, Монако) и в Алпите през зимата (ски курортите в Тарантез). Mercedes V-Class, 7 кожени места. Летищни и дълги трансфери.'};
F.bio=function(d){return (F.lang==='bg'&&(d.bio_bg||BIO[d.id]))||d.bio||'';};

/* ---------- помощни ---------- */
F.esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
F.hav=function(a,b,c,d){var R=6371,p=Math.PI/180,x=(c-a)*p,y=(d-b)*p,h=Math.sin(x/2)*Math.sin(x/2)+Math.cos(a*p)*Math.cos(c*p)*Math.sin(y/2)*Math.sin(y/2);return 2*R*Math.asin(Math.sqrt(h));};
F.name=function(d){return (F.lang==='bg'&&d.name_bg)?d.name_bg:d.name;};
F.first=function(d){return F.name(d).split(' ')[0];};
F.tel=function(d){return '+'+String(d.phone).replace(/[^0-9]/g,'');};
F.natPhone=function(p){var d=String(p||'').replace(/[^0-9]/g,'');if(d.indexOf('359')===0)return ('0'+d.slice(3)).replace(/^(\d{4})(\d{3})(\d{3})$/,'$1 $2 $3');return '+'+d;};
F.ref=function(){return F.me||{lat:F.C[0],lng:F.C[1]};};
F.km=function(d){var r=F.ref();return F.hav(r.lat,r.lng,d.lat,d.lng);};
F.near=function(d){return F.km(d)<F.NEAR_KM;};
F.mins=function(d){return Math.max(1,Math.round(F.km(d)*2.4));};
F.kmTxt=function(k){return (k<10?k.toFixed(1):String(Math.round(k))).replace('.',F.lang==='bg'?',':'.')+' '+F.t('km');};
F.byId=function(id){for(var i=0;i<F.D.length;i++)if(String(F.D[i].id)===String(id))return F.D[i];return null;};
F.toast=function(m){var el=$('toast');el.textContent=m;el.classList.add('on');clearTimeout(F._tt);F._tt=setTimeout(function(){el.classList.remove('on');},2800);};
F.buzz=function(n){try{if(navigator.vibrate)navigator.vibrate(n);}catch(e){}};
F.track=function(ev){try{var p=JSON.stringify({event:ev});if(navigator.sendBeacon)navigator.sendBeacon(F.WORKER+'/track',new Blob([p],{type:'application/json'}));else fetch(F.WORKER+'/track',{method:'POST',headers:{'Content-Type':'application/json'},body:p,keepalive:true});}catch(e){}};
F.shown=function(d){var f=F.filters;
  if(f.on&&!d.online)return false;
  if(f.en&&(d.langs||[]).indexOf('en')<0)return false;
  if(f.child&&d.childok!==true)return false;
  if(f.card&&!(d.terminal===true||(d.payment||[]).indexOf('terminal')>=0))return false;
  if(f.pet&&d.petfriendly!==true)return false;
  if(f.ev&&!d.electric)return false;
  if(f.big&&!(d.seats>=6))return false;
  return true;};

/* ---------- местоположение на клиента ---------- */
var presence=false;
F.locate=function(cb,quiet){
  if(!navigator.geolocation){if(cb)cb(null);return;}
  document.body.classList.add('locating');
  navigator.geolocation.getCurrentPosition(function(p){
    document.body.classList.remove('locating');
    F.me={lat:p.coords.latitude,lng:p.coords.longitude};
    if(!presence){presence=true;try{fetch(F.WORKER+'/presence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lat:Math.round(F.me.lat*1000)/1000,lng:Math.round(F.me.lng*1000)/1000})});}catch(e){}}
    if(F.onMe)F.onMe();if(cb)cb(F.me);
  },function(){document.body.classList.remove('locating');if(!quiet)F.toast(F.t('locDenied'));if(cb)cb(null);},
  {enableHighAccuracy:true,timeout:9000,maximumAge:60000});
};

/* ---------- данни и живи позиции ---------- */
F.lastPoll=0;
F.poll=function(){
  fetch(F.WORKER+'/gps').then(function(r){return r.json();}).then(function(data){
    F.lastPoll=Date.now();
    if(!data.ok||!data.drivers)return;
    data.drivers.forEach(function(g){
      var dr=F.D.filter(function(d){return String(d.gps_id||d.id)===String(g.driver_id);})[0];
      if(!dr)return;
      if(g.lat&&g.lng){dr.lat=g.lat;dr.lng=g.lng;}
      dr.online=!!g.online;
    });
    if(F.onData)F.onData();
  }).catch(function(){});
};
F.start=function(){
  fetch('data/drivers.json?t='+Math.floor(Date.now()/60000)).then(function(r){return r.json();}).then(function(list){
    F.D=list.filter(function(d){return d&&d.id&&d.lat&&d.lng&&d.phone;});
    F.D.forEach(function(d){d.online=false;});
    if(F.onData)F.onData(true);
    F.poll();
    setInterval(function(){if(!document.hidden)F.poll();},15000);
    document.addEventListener('visibilitychange',function(){if(!document.hidden)F.poll();});
    if(navigator.permissions&&navigator.permissions.query){navigator.permissions.query({name:'geolocation'}).then(function(st){if(st.state==='granted')F.locate(null,true);}).catch(function(){});}
  }).catch(function(){F.toast('Няма връзка. Презареди страницата.');});
};
return F;
})();
