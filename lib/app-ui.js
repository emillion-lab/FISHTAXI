/* fish.taxi v3 — екран: карта, маркери, лист със шофьори, карта на шофьора, меню. */
(function(F){
"use strict";
var $=F.$,t=F.t,esc=F.esc,map,marks={},meMark=null,visible=0;

/* ---------- карта ---------- */
function initMap(){
  map=F.map=L.map('map',{zoomControl:false,attributionControl:false,zoomSnap:.5}).setView(F.C,13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,subdomains:'abc'}).addTo(map);
  map.on('zoomstart',function(){glide(false);});
  map.on('zoomend',function(){setTimeout(function(){glide(true);},60);});
  map.on('click',function(){if(F.sel)select(null);});
}
function glide(on){for(var k in marks){var el=marks[k]._icon;if(el)el.classList.toggle('glide',on);}}
function focus(lat,lng,zoom){
  var z=zoom||Math.max(map.getZoom(),14),p=map.project([lat,lng],z);
  p.y+=Math.min(visible,innerHeight*.55)/2-20;
  map.flyTo(map.unproject(p,z),z,{duration:.7});
}
F.focus=focus;
function syncMarks(){
  F.D.forEach(function(d){
    var m=marks[d.id];
    if(!m){
      var ini=esc(F.first(d).slice(0,2).toUpperCase());
      m=marks[d.id]=L.marker([d.lat,d.lng],{icon:L.divIcon({className:'mk',iconSize:[0,0],html:'<div class="ring"></div><div class="in">'+(d.avatar?'<img src="'+esc(d.avatar)+'" alt="" onerror="this.remove()">':'')+'<span>'+ini+'</span></div><div class="tag"><span>'+esc(F.first(d))+'</span></div>'}),keyboard:false}).addTo(map);
      m.on('click',function(){select(d.id,true);});
      var im=m._icon.querySelector('img');if(im)m._icon.querySelector('.in span').style.display='none';
      setTimeout(function(){if(m._icon)m._icon.classList.add('glide');},900);
    }else m.setLatLng([d.lat,d.lng]);
    var el=m._icon;if(!el)return;
    el.classList.toggle('off',!d.online);el.classList.toggle('sel',F.sel===d.id);
    el.style.display=F.shown(d)?'':'none';
    m.setZIndexOffset(F.sel===d.id?1000:(d.online?500:0));
  });
}
F.onMe=function(){
  if(!meMark){meMark=L.marker([F.me.lat,F.me.lng],{icon:L.divIcon({className:'me',iconSize:[0,0],html:'<b></b><b></b><i></i>'}),interactive:false,zIndexOffset:800}).addTo(map);focus(F.me.lat,F.me.lng,14);}
  else meMark.setLatLng([F.me.lat,F.me.lng]);
  renderList(true);
};

/* ---------- лист ---------- */
var sheet=$('sheet'),snaps=[],snapI=1,sheetH=0,ty=0;
function measure(){
  var vh=innerHeight;sheetH=Math.round(vh*.9);sheet.style.height=sheetH+'px';
  snaps=[$('grab').offsetHeight+$('action').offsetHeight+8,Math.round(vh*.48),sheetH];
  snapTo(snapI,false);
}
function setTy(v,anim){ty=Math.max(0,Math.min(sheetH-snaps[0],v));sheet.classList.toggle('snap',!!anim);sheet.style.transform='translate3d(0,'+ty+'px,0)';visible=sheetH-ty;$('locate').style.bottom=(Math.min(visible,innerHeight*.6)+12)+'px';}
function snapTo(i,anim){snapI=i;setTy(sheetH-snaps[i],anim!==false);}
F.snapTo=snapTo;
(function(){
  var g=$('grab'),sy,st,down=false,lastY,lastT,vel=0;
  g.addEventListener('pointerdown',function(e){down=true;sy=e.clientY;st=ty;lastY=sy;lastT=e.timeStamp;vel=0;g.setPointerCapture(e.pointerId);});
  g.addEventListener('pointermove',function(e){if(!down)return;var dt=e.timeStamp-lastT;if(dt>0)vel=(e.clientY-lastY)/dt;lastY=e.clientY;lastT=e.timeStamp;setTy(st+e.clientY-sy,false);});
  function end(e){if(!down)return;down=false;
    if(Math.abs(e.clientY-sy)<5){snapTo((snapI+1)%3);return;}
    var vis=sheetH-ty-vel*160,best=0,bd=1e9;snaps.forEach(function(s,i){var dd=Math.abs(s-vis);if(dd<bd){bd=dd;best=i;}});snapTo(best);}
  g.addEventListener('pointerup',end);g.addEventListener('pointercancel',end);
})();
addEventListener('resize',measure);

var FILTERS=[['on','fOn'],['en','fEn'],['child','fChild'],['card','fCard'],['pet','fPet'],['ev','fEv'],['big','fBig']];
function renderChips(){$('chips').innerHTML=FILTERS.map(function(f){return '<button class="chip" data-f="'+f[0]+'" aria-pressed="'+(!!F.filters[f[0]])+'">'+t(f[1])+'</button>';}).join('');}
$('chips').addEventListener('click',function(e){var b=e.target.closest('.chip');if(!b)return;var k=b.dataset.f;F.filters[k]=!F.filters[k];F.buzz(8);renderChips();renderList();syncMarks();});

function etaHtml(d){
  if(!d.online)return '<span class="eta txt" data-eta>'+t('offline')+'</span>';
  if(F.me&&F.near(d))return '<span class="eta" data-eta>'+F.mins(d)+' '+t('min')+'<small>'+F.kmTxt(F.km(d))+'</small></span>';
  return '<span class="eta txt" data-eta>'+t('online')+'</span>';
}
F.etaHtml=etaHtml;
function cardHtml(d,i){
  var tags=(d.langs||[]).map(function(l){return l.toUpperCase();}).join(' · '),x=[];
  if(d.electric)x.push(t('xEv'));if(d.childok===true)x.push(t('fChild'));if(d.petfriendly===true)x.push(t('fPet'));if(d.seats>=6)x.push(d.seats+' '+t('seats').toLowerCase());
  return '<article class="card'+(d.online?'':' off')+(F.sel===d.id?' sel':'')+'" data-id="'+d.id+'" style="animation-delay:'+(i*45)+'ms">'+
   '<button class="row" aria-expanded="'+(F.sel===d.id)+'"><img class="av" src="'+esc(d.avatar||'favicon.png')+'" alt="">'+
   '<span class="who"><b><i class="dot"></i>'+esc(F.name(d))+'</b><span>'+esc(d.car)+'</span><span class="num">'+esc(d.plate)+'</span></span>'+etaHtml(d)+'</button>'+
   '<div class="more"><div><div class="tags"><span>'+tags+'</span>'+x.map(function(v){return '<span>'+esc(v)+'</span>';}).join('')+'</div>'+
   '<div class="acts"><a class="btn" href="tel:'+F.tel(d)+'" data-tr="call">'+t('call')+'</a><a class="btn" href="viber://chat?number=%2B'+F.tel(d).slice(1)+'" data-tr="viber">Viber</a>'+
   '<button class="btn wide" data-a="more">'+t('details')+'</button><button class="btn wide go" data-a="order">'+t('orderAt')+' '+esc(F.first(d))+'</button></div></div></div></article>';
}
var lastSig='';
function sig(){return F.lang+'|'+F.sel+'|'+(F.me?1:0)+'|'+F.D.filter(F.shown).map(function(d){return d.id+(d.online?'+':'-');}).join(',');}
function order(a,b){return (b.online-a.online)||(F.km(a)-F.km(b));}
function renderList(soft){
  var arr=F.D.filter(F.shown),near=arr.filter(F.near).sort(order),far=arr.filter(function(d){return !F.near(d);}).sort(order);
  var on=near.filter(function(d){return d.online;}).length;
  $('count').textContent=on?on+' '+t(on===1?'free1':'free'):t('none');
  var s=sig();
  if(soft&&s===lastSig){arr.forEach(function(d){var c=$('list').querySelector('[data-id="'+d.id+'"] [data-eta]');if(!c)return;var o=c.textContent;c.outerHTML=etaHtml(d);var n=$('list').querySelector('[data-id="'+d.id+'"] [data-eta]');if(n.textContent!==o)n.classList.add('tick');});return;}
  lastSig=s;
  if(!arr.length){$('list').innerHTML='<div class="empty">'+t(F.D.length?'noMatch':'noDrivers')+'</div>';return;}
  $('list').innerHTML=(on?'':'<p class="hint">'+t('offHint')+'</p>')+near.map(cardHtml).join('')+(far.length?'<div class="sep">'+t('other')+'</div>'+far.map(cardHtml).join(''):'')+'<p class="note">'+t('about')+'<br>'+t('osm')+'</p>';
}
$('list').addEventListener('click',function(e){
  var card=e.target.closest('.card');if(!card)return;var d=F.byId(card.dataset.id);
  var tr=e.target.closest('[data-tr]');if(tr){F.track(tr.dataset.tr);return;}
  var a=e.target.closest('[data-a]');
  if(a){if(a.dataset.a==='more')openProf(d);else if(F.openOrder)F.openOrder(d);return;}
  select(F.sel===d.id?null:d.id,false);
});
function select(id,fromMap){
  F.sel=id;F.buzz(8);syncMarks();renderList();
  if(!id)return;var d=F.byId(id);
  if(fromMap){if(snapI!==1)snapTo(1);focus(d.lat,d.lng);}else if(snapI<2)snapTo(2);
  setTimeout(function(){var c=$('list').querySelector('[data-id="'+id+'"]'),Ls=$('list');if(c)Ls.scrollTo({top:Math.max(0,c.offsetTop-Ls.offsetTop-4),behavior:'smooth'});},40);
}
F.select=select;

/* ---------- панели ---------- */
/* „Назад“ на телефона затваря панела, вместо да излиза от приложението */
var pushed=false;
function openPanel(id){closePanels(true);$(id).classList.add('open');$(id).style.transform='';document.body.classList.add('popen');F.buzz(10);
  if(!pushed){try{history.pushState({ftp:1},'',location.href);pushed=true;}catch(e){}}}
function closePanels(keep){[].forEach.call(document.querySelectorAll('.panel.open'),function(p){p.classList.remove('open');p.style.transform='';});
  if(keep)return;
  document.body.classList.remove('popen');
  if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();
  if(pushed){pushed=false;if(history.state&&history.state.ftp){history.back();return;}}
  if(/^#d\d+$/.test(location.hash))history.replaceState(null,'',location.pathname+location.search);}
addEventListener('popstate',function(){if(pushed){pushed=false;closePanels();}});
F.openPanel=openPanel;F.closePanels=closePanels;
$('dim').onclick=function(){closePanels();};
[].forEach.call(document.querySelectorAll('.panel'),function(P){
  P.querySelector('.pclose').onclick=function(){closePanels();};
  var tp=P.querySelector('.ptop'),sy,dy=0,down=false;
  tp.addEventListener('pointerdown',function(e){down=true;sy=e.clientY;dy=0;P.classList.add('drag');tp.setPointerCapture(e.pointerId);});
  tp.addEventListener('pointermove',function(e){if(!down)return;dy=Math.max(0,e.clientY-sy);P.style.transform='translateY('+dy+'px)';});
  function end(){if(!down)return;down=false;P.classList.remove('drag');if(dy>90)closePanels();else P.style.transform='';}
  tp.addEventListener('pointerup',end);tp.addEventListener('pointercancel',end);
});

/* ---------- карта на шофьора ---------- */
var GEN={pop:['Поп','Pop'],rock:['Рок','Rock'],classical:['Класика','Classical'],jazz:['Джаз','Jazz'],electronic:['Електронна','Electronic'],chillout:['Чилаут','Chillout'],lounge:['Лаундж','Lounge'],chalga:['Чалга','Chalga']};
function tri(v){return v===true?t('yes'):(v==='ask'?t('ask'):t('no'));}
function eur(n){return n.toFixed(2).replace('.',F.lang==='bg'?',':'.')+' €';}
function row(k,v){return '<div class="prow"><span>'+t(k)+'</span><b>'+v+'</b></div>';}
function openProf(d){
  var ph=(d.photos||[]).slice();if(d.tariff_photo)ph.push(d.tariff_photo);
  $('pgal').innerHTML=ph.map(function(p,i){return '<img src="'+esc(p)+'" alt="" '+(i?'loading="lazy"':'')+'>';}).join('');
  $('pgal').style.display=ph.length?'':'none';$('pgal').scrollLeft=0;dots(0,ph.length);
  var mus=d.nomusic?t('noMusic'):Object.keys(GEN).filter(function(g){return d['music_'+g];}).map(function(g){return GEN[g][F.lang==='bg'?0:1];}).join(', ')||t('anyMusic');
  var tar=d.tariff?t('start')+' '+eur(d.tariff.start)+' · '+t('day')+' '+eur(d.tariff.km_day)+'/'+t('km')+' · '+t('night')+' '+eur(d.tariff.km_night)+'/'+t('km'):t('onreq');
  var x=[['verified','xVer'],['electric','xEv'],['nosmoker','xNos'],['ac','xAc'],['usb','xUsb'],['streaming','xStream'],['panoroof','xRoof'],['legroom','xLeg'],['tinted','xTint'],['silent_ok','xQuiet']].filter(function(p){return d[p[0]]===true;}).map(function(p){return '<span>'+t(p[1])+'</span>';}).join('');
  $('pbody').innerHTML=
   '<div class="phead"><img class="av" src="'+esc(d.avatar||'favicon.png')+'" alt=""><h2>'+esc(F.name(d))+'</h2><p class="'+(d.online?'':'off')+'"><i class="dot"></i>'+t(d.online?'online':'offline')+'</p>'+etaHtml(d).replace(' data-eta','')+'</div>'+
   '<div class="pgrp">'+row('car',esc(d.car))+row('plate','<span class="num" style="margin:0">'+esc(d.plate)+'</span>')+row('seats',d.seats)+row('tariff',tar)+row('pay',(d.payment||[]).map(function(p){return t(p);}).join(', '))+'</div>'+
   '<div class="pgrp">'+row('music',mus)+row('langs',(d.langs||[]).map(function(l){return F.LN[l]||l;}).join(', '))+row('pets',tri(d.petfriendly))+row('child',tri(d.childok))+'</div>'+
   '<div class="pgrp">'+row('airport',tri(d.airport))+row('longd',tri(d.longdist))+row('nightw',tri(d.night))+row('wheel',tri(d.wheelchair))+'</div>'+
   (x?'<div class="pgrp"><div class="pchips">'+x+'</div></div>':'')+
   (F.bio(d)?'<div class="pgrp"><div class="pbio">'+esc(F.bio(d))+'</div></div>':'')+
   '<div class="pgrp">'+row('areas',esc(d.areas||''))+row('phone','<a href="tel:'+F.tel(d)+'">'+F.natPhone(d.phone)+'</a>')+'</div>';
  $('pbody').scrollTop=0;
  $('pact').innerHTML='<a class="btn" href="tel:'+F.tel(d)+'" data-tr="call">'+t('call')+'</a><button class="btn" data-a="share">'+t('share')+'</button><button class="btn wide go" data-a="order">'+t('orderAt')+' '+esc(F.first(d))+'</button>';
  $('pact').dataset.id=d.id;
  openPanel('prof');try{history.replaceState(history.state,'','#d'+d.id);}catch(e){}
  F.track('open_driver');
}
F.openProf=openProf;
function dots(n,len){$('pdots').innerHTML=len>1?Array.apply(null,Array(len)).map(function(_,i){return '<i class="'+(i===n?'on':'')+'"></i>';}).join(''):'';}
$('pgal').addEventListener('scroll',function(){dots(Math.round(this.scrollLeft/this.clientWidth),this.children.length);},{passive:true});
$('pact').addEventListener('click',function(e){
  var d=F.byId(this.dataset.id);if(!d)return;
  var tr=e.target.closest('[data-tr]');if(tr){F.track(tr.dataset.tr);return;}
  var a=e.target.closest('[data-a]');if(!a)return;
  if(a.dataset.a==='order'){if(F.openOrder)F.openOrder(d);return;}
  var url=location.origin+location.pathname+'#d'+d.id;
  if(navigator.share){navigator.share({title:'fish.taxi — '+F.name(d),url:url}).catch(function(){});}
  else{try{navigator.clipboard.writeText(url);F.toast(t('copied'));}catch(er){F.toast(url);}}
});

/* ---------- меню ---------- */
function renderMenu(){
  var classic=/app\.html$/.test(location.pathname)?'./':'classic.html';
  $('mbody').innerHTML='<div class="pgrp"><h3>'+t('lang')+'</h3><div class="seg">'+['bg','en'].map(function(l){return '<button class="chip" data-l="'+l+'" aria-pressed="'+(F.lang===l)+'">'+F.LN[l]+'</button>';}).join('')+'</div></div>'+
   '<div class="pgrp"><a class="mrow" href="join.html">'+t('join')+'<small>›</small></a><a class="mrow" href="'+classic+'">'+t('classic')+'<small>›</small></a></div>'+
   '<p class="note">'+t('about')+'<br>'+t('osm')+'</p>';
}
$('menuBtn').onclick=function(){renderMenu();openPanel('menu');};
$('mbody').addEventListener('click',function(e){var b=e.target.closest('[data-l]');if(!b)return;F.setLang(b.dataset.l);texts();renderMenu();});

/* ---------- горна табелка ---------- */
function hud(){
  $('hOn').textContent=F.D.filter(function(d){return d.online;}).length;$('hOnT').textContent=' '+t('online');
  var s=F.lastPoll?Math.round((Date.now()-F.lastPoll)/1000):null;
  $('hAge').textContent=s===null?'…':t('updated')+' '+(s<3?t('now'):(t('ago')+' '+s+' '+t('sec')).trim());
}
function texts(){
  $('levTxt').textContent=t('slide');$('knob').setAttribute('aria-label',t('slide'));$('menuBtn').setAttribute('aria-label',t('menu'));
  renderChips();lastSig='';renderList();hud();measure();
}
F.texts=texts;

/* ---------- лост за поръчка ---------- */
(function(){
  var Lv=$('lever'),K=$('knob'),Fl=Lv.querySelector('.fill'),T=$('levTxt'),sx,down=false,x=0,max=0;
  function set(v){x=Math.max(0,Math.min(max,v));K.style.transform='translate3d('+x+'px,0,0)';Fl.style.width=x?(x+44)+'px':'0';T.style.opacity=max?1-x/max*1.2:1;}
  function fire(){F.buzz([12,40,30]);if(F.quickOrder)F.quickOrder();setTimeout(function(){K.classList.add('back');set(0);},500);}
  K.addEventListener('pointerdown',function(e){down=true;max=Lv.clientWidth-K.offsetWidth-10;sx=e.clientX-x;K.classList.remove('back');K.setPointerCapture(e.pointerId);});
  K.addEventListener('pointermove',function(e){if(down)set(e.clientX-sx);});
  function end(){if(!down)return;down=false;if(x>=max*.85)fire();else{K.classList.add('back');set(0);}}
  K.addEventListener('pointerup',end);K.addEventListener('pointercancel',end);
  K.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();fire();}});
})();
$('locate').onclick=function(){if(F.me)focus(F.me.lat,F.me.lng,15);F.locate(function(m){if(m)focus(m.lat,m.lng,15);});};

/* ---------- старт ---------- */
F.onData=function(first){
  syncMarks();hud();renderList(!first);
  if(first){var m=/^#d(\d+)$/.exec(location.hash||'');if(m){var d=F.byId(m[1]);if(d)setTimeout(function(){openProf(d);},500);}}
};
document.documentElement.lang=F.lang;
initMap();texts();setInterval(hud,1000);
map.whenReady(function(){setTimeout(function(){focus(F.C[0],F.C[1],13);},50);});
F.start();
})(FT);
