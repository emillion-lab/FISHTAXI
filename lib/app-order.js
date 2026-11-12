/* fish.taxi v3 — поръчка: събира данните и отваря SMS, Viber, WhatsApp или обаждане към шофьора. */
(function(F){
"use strict";
var $=F.$,t=F.t,esc=F.esc,O=null;

/* Текстът до шофьора е на език, който той говори (иначе на английски). */
var OT={
 bg:{head:'🚕 fish.taxi — ПОРЪЧКА',now:'🕒 Сега (веднага)',when:'📅 Желан час:',note:'⚠️ Моля, потвърдете с отговор.',pax:'• Пътници: ',prefs:'Желания:',myloc:'📍 Моята локация:',nogps:'📍 Локация: ще я пратя в чата (няма GPS)',dest:'🏁 Докъде:',route:'🗺 Маршрут:',confirm:'☎️ Потвърждение на този номер.'},
 en:{head:'🚕 fish.taxi — ORDER',now:'🕒 Now (immediately)',when:'📅 Requested time:',note:'⚠️ Please confirm by replying.',pax:'• Passengers: ',prefs:'Wishes:',myloc:'📍 My location:',nogps:'📍 Location: will send in chat (no GPS)',dest:'🏁 Destination:',route:'🗺 Route:',confirm:'☎️ Confirm on this number.'},
 de:{head:'🚕 fish.taxi — BESTELLUNG',now:'🕒 Jetzt (sofort)',when:'📅 Gewünschte Zeit:',pax:'• Fahrgäste: ',prefs:'Wünsche:',myloc:'📍 Mein Standort:',nogps:'📍 Standort: sende ich im Chat (kein GPS)',dest:'🏁 Ziel:',route:'🗺 Route:',confirm:'☎️ Bestätigung unter dieser Nummer.'},
 fr:{head:'🚕 fish.taxi — COMMANDE',now:'🕒 Maintenant (immédiatement)',when:'📅 Heure souhaitée :',pax:'• Passagers : ',prefs:'Préférences :',myloc:'📍 Ma position :',nogps:'📍 Position : je l’envoie dans le chat (pas de GPS)',dest:'🏁 Destination :',route:'🗺 Itinéraire :',confirm:'☎️ Confirmation à ce numéro.'},
 ru:{head:'🚕 fish.taxi — ЗАКАЗ',now:'🕒 Сейчас (сразу)',when:'📅 Желаемое время:',pax:'• Пассажиры: ',prefs:'Пожелания:',myloc:'📍 Моё местоположение:',nogps:'📍 Место: пришлю в чат (нет GPS)',dest:'🏁 Куда:',route:'🗺 Маршрут:',confirm:'☎️ Подтверждение на этот номер.'},
 it:{head:'🚕 fish.taxi — ORDINE',now:'🕒 Ora (subito)',when:'📅 Orario richiesto:',pax:'• Passeggeri: ',prefs:'Preferenze:',myloc:'📍 La mia posizione:',nogps:'📍 Posizione: la invio in chat (niente GPS)',dest:'🏁 Destinazione:',route:'🗺 Percorso:',confirm:'☎️ Conferma a questo numero.'},
 es:{head:'🚕 fish.taxi — PEDIDO',now:'🕒 Ahora (inmediatamente)',when:'📅 Hora solicitada:',pax:'• Pasajeros: ',prefs:'Preferencias:',myloc:'📍 Mi ubicación:',nogps:'📍 Ubicación: la enviaré en el chat (sin GPS)',dest:'🏁 Destino:',route:'🗺 Ruta:',confirm:'☎️ Confirmación a este número.'}
};
var PREFS=[['quiet','pQuiet','Предпочитам тишина','Prefer silence'],['talk','pTalk','Готов за разговор','Happy to chat'],['calm','pCalm','Моля, карайте спокойно','Please drive calmly'],['music','pMusic','Музика','Music please'],['bag','pBag','Голям багаж','Large luggage']];
function oLang(d){return (d.langs||[]).indexOf(F.lang)>=0?F.lang:'en';}
function isNight(){var h=new Date().getHours();return h>=22||h<6;}
function price(km,d){if(!d.tariff)return null;var n=isNight(),st=(n&&d.tariff.start_night)?d.tariff.start_night:d.tariff.start;return Math.round((st+km*(n?d.tariff.km_night:d.tariff.km_day))*10)/10;}

function estimate(a,b,cb){
  var done=false,fb=F.hav(a.lat,a.lng,b.lat,b.lng)*1.35;
  function fin(km,min){if(done)return;done=true;clearTimeout(tm);cb({km:Math.round(km*10)/10,min:Math.round(min)});}
  var tm=setTimeout(function(){fin(fb,fb/.42);},2500);
  try{fetch('https://router.project-osrm.org/route/v1/driving/'+a.lng+','+a.lat+';'+b.lng+','+b.lat+'?overview=false').then(function(r){return r.json();})
    .then(function(d){if(d.routes&&d.routes[0])fin(d.routes[0].distance/1000,d.routes[0].duration/60+3);else fin(fb,fb/.42);}).catch(function(){fin(fb,fb/.42);});}catch(e){fin(fb,fb/.42);}
}
function estLine(){
  if(!O.est)return '';
  var p=price(O.est.km,O.d);
  return '≈ '+F.kmTxt(O.est.km)+' · ~'+O.est.min+' '+t('min')+(p?' · ~'+p.toFixed(2).replace('.',F.lang==='bg'?',':'.')+' €':'');
}
function refreshEst(){
  O.est=null;$('oEst').textContent='';
  if(!O.to||!F.me)return;
  var o=O;estimate(F.me,O.to,function(e){if(O!==o)return;O.est=e;$('oEst').textContent=estLine();});
}

function message(){
  var d=O.d,l=oLang(d),m=OT[l]||OT.en,g=function(k){return m[k]||OT.en[k];},L=[];
  L.push(g('head')+(l===F.lang?'':' ['+F.lang.toUpperCase()+']'));L.push('');
  if(O.when==='later'&&$('oDt').value){var v=$('oDt').value.split('T'),dp=v[0].split('-');L.push(g('when')+' '+dp[2]+'.'+dp[1]+'.'+dp[0]+' '+(v[1]||''));L.push(g('note'));}
  else L.push(g('now'));
  L.push(g('pax')+O.pax);
  if(O.prefs.length){L.push(g('prefs'));PREFS.forEach(function(p){if(O.prefs.indexOf(p[0])>=0)L.push('• '+(l==='bg'?p[2]:p[3]));});}
  L.push('');
  if(F.me){L.push(g('myloc'));L.push('https://maps.google.com/?q='+F.me.lat.toFixed(6)+','+F.me.lng.toFixed(6));}
  else L.push(g('nogps'));
  if(O.to){
    L.push('');L.push(g('dest')+' '+O.to.label);L.push('https://maps.google.com/?q='+O.to.lat.toFixed(6)+','+O.to.lng.toFixed(6));
    if(F.me){L.push(g('route'));L.push('https://www.google.com/maps/dir/?api=1&origin='+F.me.lat.toFixed(6)+','+F.me.lng.toFixed(6)+'&destination='+O.to.lat.toFixed(6)+','+O.to.lng.toFixed(6)+'&travelmode=driving');
      if(O.est){var p=price(O.est.km,d);L.push('≈ '+O.est.km+' km · ~'+O.est.min+' min'+(p?' · ~'+p+' €':''));}}
  }
  L.push('');L.push(g('confirm'));
  return L.join('\n');
}
F._orderMessage=message;

function locRow(){
  var el=$('oLoc');if(!el)return;
  if(F.me)el.innerHTML='<span>'+t('pickup')+'</span><b>'+t('locOk')+' ✓</b>';
  else if(document.body.classList.contains('locating'))el.innerHTML='<span>'+t('pickup')+'</span><b>'+t('locWait')+'</b>';
  else el.innerHTML='<span>'+t('locNo')+'</span><b><button class="chip" data-a="retry">'+t('retry')+'</button></b>';
}
function findMe(){F.locate(function(){if(!O)return;locRow();refreshEst();},true);locRow();}

function openOrder(d){
  O={d:d,when:'now',pax:'1-2',prefs:[],to:null,est:null};
  var pax=['1-2','3','4'];for(var n=5;n<=(d.seats||4);n++)pax.push(String(n));pax=pax.filter(function(p){return p==='1-2'||parseInt(p,10)<=(d.seats||4);});
  var dt=new Date(Date.now()+3600e3-new Date().getTimezoneOffset()*60e3).toISOString().slice(0,16);
  function seg(name,items,cur){return '<div class="seg" data-seg="'+name+'">'+items.map(function(i){return '<button class="chip" data-v="'+i[0]+'" aria-pressed="'+(cur.indexOf(i[0])>=0)+'">'+i[1]+'</button>';}).join('')+'</div>';}
  $('obody').innerHTML=
   '<div class="phead"><img class="av" src="'+esc(d.avatar||'favicon.png')+'" alt=""><h2>'+t('oTitle')+' '+esc(F.first(d))+'</h2><p>'+esc(d.car)+' · '+esc(d.plate)+'</p></div>'+
   (d.online?'':'<p class="note" style="text-align:left;padding:0 2px 10px">'+t('notOnline')+'</p>')+
   '<div class="pgrp"><div class="prow" id="oLoc"></div></div>'+
   '<div class="pgrp"><h3>'+t('when')+'</h3>'+seg('when',[['now',t('wNow')],['later',t('wLater')]],['now'])+'<input class="fld" id="oDt" type="datetime-local" value="'+dt+'" style="display:none"></div>'+
   '<div class="pgrp"><h3>'+t('pax')+'</h3>'+seg('pax',pax.map(function(p){return [p,p];}),['1-2'])+'</div>'+
   '<div class="pgrp"><h3>'+t('wishes')+'</h3>'+seg('prefs',PREFS.map(function(p){return [p[0],t(p[1])];}),[])+'</div>'+
   '<div class="pgrp"><h3>'+t('dest')+'</h3><div style="height:10px"></div><input class="fld" id="oTo" type="search" autocomplete="off" placeholder="'+t('destPh')+'"><div class="sug" id="oSug"></div><div class="est" id="oEst"></div></div>';
  $('obody').scrollTop=0;
  $('oact').innerHTML='<button class="btn wide go" data-s="sms">'+t('sms')+'</button><button class="btn" data-s="viber">'+t('viber')+'</button><button class="btn" data-s="wa">'+t('wa')+'</button><a class="btn wide" href="tel:'+F.tel(d)+'" data-s="call">'+t('call')+' · '+F.natPhone(d.phone)+'</a>';
  F.openPanel('ord');F.track('order_open');
  findMe();
}
F.openOrder=openOrder;

$('obody').addEventListener('click',function(e){
  if(!O)return;
  if(e.target.closest('[data-a="retry"]')){findMe();return;}
  var s=e.target.closest('#oSug button');
  if(s){O.to={lat:+s.dataset.lat,lng:+s.dataset.lng,label:s.dataset.label};$('oTo').value=O.to.label;$('oSug').innerHTML='';$('oTo').blur();refreshEst();return;}
  var b=e.target.closest('.seg .chip');if(!b)return;
  var name=b.parentNode.dataset.seg,v=b.dataset.v;F.buzz(8);
  if(name==='prefs'){var i=O.prefs.indexOf(v);if(i>=0)O.prefs.splice(i,1);else O.prefs.push(v);b.setAttribute('aria-pressed',i<0);return;}
  O[name]=v;[].forEach.call(b.parentNode.children,function(c){c.setAttribute('aria-pressed',c===b);});
  if(name==='when')$('oDt').style.display=v==='later'?'':'none';
});
/* Адреси: близки места веднага, после търсене само около клиента (~50 км, Photon). */
var PLACES=[
['НДК','Национален дворец на културата, София',42.6857,23.3190,'ндк ndk дворец palace culture'],
['Летище София','Терминал 1 и 2, София',42.6952,23.4064,'летище аерогара airport sofia терминал'],
['Централна гара','Гара София',42.7122,23.3210,'гара централна railway station'],
['Автогара Сердика','Централна автогара, София',42.7117,23.3209,'автогара сердика bus station'],
['Александър Невски','Храм-паметник, София',42.6957,23.3327,'александър невски катедрала cathedral'],
['Парадайс център','бул. Черни връх, София',42.6573,23.3153,'парадайс paradise mall'],
['Национален стадион Васил Левски','София',42.6853,23.3347,'стадион левски stadium'],
['Алеко, Витоша','Ски зона, Витоша',42.5606,23.2907,'алеко витоша vitosha ski']];
function dkm(a,b,c,d){var x=(c-a)*111.2,y=(d-b)*111.2*Math.cos(a*Math.PI/180);return Math.sqrt(x*x+y*y);}
function sugBtn(i){return '<button data-lat="'+i.lat+'" data-lng="'+i.lng+'" data-label="'+esc(i.label)+'">'+esc(i.name)+'<small>'+esc(i.sub)+'</small></button>';}
function fromFeat(f){
  var p=f.properties||{},c=f.geometry.coordinates,st=[p.street,p.housenumber].filter(Boolean).join(' '),name=p.name||st||p.city||'';
  if(!name)return null;
  return {lat:c[1],lng:c[0],name:name,label:name+(p.city&&p.city!==name?', '+p.city:''),sub:[p.name?st:'',p.city,p.country].filter(Boolean).join(', ')};
}
function localHits(q){
  var r=F.ref(),ql=q.toLowerCase();
  return PLACES.map(function(p){return {lat:p[2],lng:p[3],name:p[0],label:p[0],sub:p[1],d:dkm(r.lat,r.lng,p[2],p[3]),h:(p[0]+' '+p[4]).toLowerCase()};})
   .filter(function(p){return p.d<60&&(!ql||p.h.indexOf(ql)>=0);}).sort(function(a,b){return a.d-b.d;}).slice(0,ql?4:5);
}
function showSug(items){$('oSug').innerHTML=items.map(sugBtn).join('');keepVisible();}
function keepVisible(){
  var b=$('obody'),i=$('oTo');if(!b||!i||document.activeElement!==i)return;
  b.scrollTop+=i.getBoundingClientRect().top-b.getBoundingClientRect().top-10;
}
var st,seq=0;
function search(q){
  var my=++seq,r=F.ref(),loc=localHits(q),base='https://photon.komoot.io/api/?q='+encodeURIComponent(q)+'&lat='+r.lat+'&lon='+r.lng;
  showSug(loc);
  function get(url){return fetch(url).then(function(x){return x.json();}).then(function(j){return (j.features||[]).map(fromFeat).filter(Boolean);});}
  function merge(a){
    var seen={};loc.forEach(function(x){seen[x.name.toLowerCase()]=1;});
    return loc.concat(a.filter(function(x){var k=x.name.toLowerCase();if(seen[k])return false;seen[k]=1;return true;})).slice(0,8);
  }
  get(base+'&limit=10&bbox='+[r.lng-.6,r.lat-.45,r.lng+.6,r.lat+.45].join(','))
   .then(function(a){if(my===seq&&O)showSug(merge(a));}).catch(function(){});
}
$('obody').addEventListener('input',function(e){
  if(e.target.id!=='oTo'||!O)return;
  var q=e.target.value.trim();clearTimeout(st);
  if(O.to&&q!==O.to.label){O.to=null;O.est=null;$('oEst').textContent='';}
  if(q.length<2){seq++;showSug(localHits(''));return;}
  if(q.length<3){showSug(localHits(q));return;}
  st=setTimeout(function(){search(q);},300);
});
$('obody').addEventListener('focusin',function(e){
  if(e.target.id!=='oTo'||!O)return;
  var q=e.target.value.trim();
  if(!O.to&&q.length<3)showSug(localHits(q));
  setTimeout(keepVisible,350);
});
/* клавиатурата: панелът се вдига над нея */
function kbFit(){
  var v=window.visualViewport,p=$('ord');if(!v||!p)return;
  var kb=Math.max(0,Math.round(window.innerHeight-v.height-v.offsetTop));
  p.style.setProperty('--kb',kb+'px');p.classList.toggle('kbd',kb>80);
  if(kb>80&&document.activeElement&&document.activeElement.id==='oTo')setTimeout(keepVisible,60);
}
if(window.visualViewport){visualViewport.addEventListener('resize',kbFit);visualViewport.addEventListener('scroll',kbFit);}

$('oact').addEventListener('click',function(e){
  var b=e.target.closest('[data-s]');if(!b||!O)return;
  var how=b.dataset.s,d=O.d,num=F.tel(d);F.track('order_'+how);
  if(how==='call')return;
  var msg=message();F.buzz([20,60,20]);
  if(how==='sms'){location.href='sms:'+num+(/iPhone|iPad|iPod/i.test(navigator.userAgent)?'&':'?')+'body='+encodeURIComponent(msg);}
  else if(how==='wa'){location.href='https://wa.me/'+num.slice(1)+'?text='+encodeURIComponent(msg);}
  else{try{navigator.clipboard.writeText(msg);}catch(er){}F.toast(t('vCopied'));setTimeout(function(){location.href='viber://chat?number=%2B'+num.slice(1);},700);}
});

/* Лостът: най-близкият онлайн шофьор наблизо; ако няма онлайн, най-близкият. */
F.quickOrder=function(){
  var c=F.D.filter(function(d){return F.shown(d)&&F.near(d);}).sort(function(a,b){return (b.online-a.online)||(F.km(a)-F.km(b));});
  if(!c.length){F.toast(t('noDrivers'));return;}
  F.track('order_simple');F.select(c[0].id,true);openOrder(c[0]);
};
})(FT);
