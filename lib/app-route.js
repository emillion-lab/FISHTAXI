/* fish.taxi v3.4 — задръж пръст върху картата → дестинация и до 3 маршрута (като Waze).
 * Маршрутите са от OSRM (безплатно, без ключ). OSRM не знае трафика на живо —
 * времената са за нормално движение; това пише и под маршрутите.
 */
(function(F){
"use strict";
var $=F.$,esc=F.esc,map=F.map,R=null,lines=[],pin=null,pushed=false,seq=0;
function T(bg,en){return F.lang==='bg'?bg:en;}
function isNight(){var h=new Date().getHours();return h>=22||h<6;}
function price(km,d){if(!d||!d.tariff)return null;var n=isNight(),s=(n&&d.tariff.start_night)?d.tariff.start_night:d.tariff.start;return Math.round((s+km*(n?d.tariff.km_night:d.tariff.km_day))*10)/10;}
function eur(p){return p.toFixed(2).replace('.',F.lang==='bg'?',':'.')+' €';}
function km(m){return F.kmTxt(m/1000);}
/* шофьорите, от които клиентът избира: наблизо (с филтрите), онлайн първи; ако няма наблизо — всички */
function drivers(){
  var c=F.D.filter(function(d){return F.shown(d)&&F.near(d);});if(!c.length)c=F.D.filter(F.shown);if(!c.length)c=F.D.slice();
  return c.sort(function(a,b){return (b.online-a.online)||(F.km(a)-F.km(b));});
}
/* цена „от–до“ по тарифите на шофьорите наблизо */
function range(km){
  var ps=drivers().map(function(d){return price(km,d);}).filter(function(p){return p!=null;});if(!ps.length)return '';
  var lo=Math.min.apply(null,ps),hi=Math.max.apply(null,ps);
  return '~'+(Math.abs(hi-lo)<.5?eur(lo):eur(lo).replace(' €','')+'–'+eur(hi));
}
var FLAG={bg:'🇧🇬',en:'🇬🇧',ru:'🇷🇺',de:'🇩🇪',fr:'🇫🇷',tr:'🇹🇷',it:'🇮🇹',es:'🇪🇸',cs:'🇨🇿',ar:'🇸🇦',zh:'🇨🇳'};
function icons(d){
  var x=(d.langs||[]).map(function(l){return FLAG[l]||l.toUpperCase();});
  if(d.nosmoker===true)x.push('🚭');if(d.ac===true)x.push('❄️');if(d.electric)x.push('⚡');
  if(d.petfriendly===true)x.push('🐾');if(d.childok===true)x.push('👶');
  if((d.payment||[]).some(function(p){return p==='terminal'||p==='card'||p==='revolut';}))x.push('💳');
  return x.join(' ');
}

var card=document.createElement('section');card.id='rcard';card.className='glassy';card.setAttribute('aria-live','polite');document.body.appendChild(card);

function color(sel){var day=document.documentElement.classList.contains('day');return sel?(day?'#9a7424':'#e6c36a'):(day?'rgba(70,80,90,.55)':'rgba(170,180,190,.6)');}
function draw(){
  lines.forEach(function(l){map.removeLayer(l);});lines=[];
  if(!R||!R.routes.length)return;
  var order=R.routes.map(function(_,i){return i;}).sort(function(a,b){return (a===R.sel)-(b===R.sel);});
  order.forEach(function(i){
    var r=R.routes[i],ll=r.geometry.coordinates.map(function(c){return [c[1],c[0]];}),sel=i===R.sel;
    var casing=L.polyline(ll,{color:'rgba(0,0,0,.45)',weight:sel?10:8,opacity:1,interactive:false}).addTo(map);
    var ln=L.polyline(ll,{color:color(sel),weight:sel?6:5,opacity:1,lineCap:'round'}).addTo(map);
    ln.on('click',function(e){L.DomEvent.stop(e);choose(i);});
    lines.push(casing,ln);
  });
}
function fit(){
  if(!R)return;var pts=[[R.to.lat,R.to.lng],[R.from.lat,R.from.lng]];
  R.routes.forEach(function(r){r.geometry.coordinates.forEach(function(c,i){if(i%8===0)pts.push([c[1],c[0]]);});});
  var ch=card.offsetHeight||220;document.body.style.setProperty('--rh',ch+'px');
  map.flyToBounds(pts,{paddingTopLeft:[30,90],paddingBottomRight:[30,ch+40],duration:.7,maxZoom:16});
}
function render(){
  if(!R)return;
  if(R.view==='pick')return renderPick();
  var ds=drivers(),list;
  if(R.wait)list='<div class="rwait">'+T('Търся маршрути…','Finding routes…')+'</div>';
  else if(!R.routes.length)list='<div class="rwait">'+T('Няма маршрут до тази точка. Пробвай малко по-близо до път.','No route to this point. Try a bit closer to a road.')+'</div>';
  else list='<div class="rlist">'+R.routes.map(function(r,i){
    var p=range(r.distance/1000),tag=[];
    if(i===R.fast)tag.push(T('⚡ Най-бърз','⚡ Fastest'));
    if(i===R.short&&R.short!==R.fast)tag.push(T('📏 Най-къс','📏 Shortest'));
    if(i===R.short&&R.short===R.fast&&R.routes.length>1)tag.push(T('📏 и най-къс','📏 and shortest'));
    if(!tag.length)tag.push(T('Друг път','Other route'));
    return '<button class="rt" data-i="'+i+'" aria-pressed="'+(i===R.sel)+'" style="animation-delay:'+(i*60)+'ms"><b>'+Math.round(r.duration/60+3)+' '+T('мин','min')+'</b><span>'+km(r.distance)+'</span>'+(p?'<span>'+p+'</span>':'')+'<em>'+tag.join(' ')+'</em></button>';
  }).join('')+'</div>';
  card.innerHTML='<button class="x" aria-label="'+T('Затвори','Close')+'">×</button>'+
   '<div class="rto"><span>🏁 '+T('Докъде','Where to')+(R.from.me?'':' · '+T('от центъра (няма GPS)','from the centre (no GPS)'))+'</span><b>'+esc(R.to.label)+'</b></div>'+list+
   (ds.length?'<button class="btn wide go" data-a="order">'+T('Поръчай до тук','Order to here')+'</button>':'<p class="note">'+T('Няма шофьор наблизо.','No driver nearby.')+'</p>')+
   (R.routes.length?'<p class="note">'+T('Времената са за нормално движение, без трафик на живо.','Times assume normal traffic, not live.')+'</p>':'');
  document.body.style.setProperty('--rh',card.offsetHeight+'px');
}
function renderPick(){
  var r=R.routes[R.sel],ds=drivers();
  card.innerHTML='<button class="x" aria-label="'+T('Затвори','Close')+'">×</button>'+
   '<div class="rto"><button class="pback" data-a="back" aria-label="'+T('Назад','Back')+'">‹</button><span>'+T('Избери шофьор до','Choose a driver to')+'</span><b>'+esc(R.to.label)+'</b></div>'+
   '<div class="plist">'+ds.map(function(d,i){
     var p=r?price(r.distance/1000,d):null,car=(d.photos||[])[0];
     var st=d.online?(F.me&&F.near(d)?'<i class="on"></i>~'+F.mins(d)+' '+T('мин до теб','min away'):'<i class="on"></i>'+T('онлайн','online')):'<i></i>'+T('офлайн','offline');
     return '<button class="pk'+(d.online?'':' off')+'" data-id="'+d.id+'" style="animation-delay:'+(i*50)+'ms">'+
      '<span class="ph">'+(car?'<img class="pc" src="'+esc(car)+'" alt="" loading="lazy">':'')+'<img class="pa" src="'+esc(d.avatar||'favicon.png')+'" alt=""></span>'+
      '<span class="pi"><b>'+esc(F.name(d))+'</b><span>'+esc(d.car||'')+(d.seats>=6?' · '+d.seats+' '+T('места','seats'):'')+'</span><em>'+icons(d)+'</em></span>'+
      '<span class="pp">'+(p?'<b>~'+eur(p)+'</b>':'')+'<small>'+st+'</small></span></button>';
   }).join('')+'</div>'+
   '<p class="note">'+T('Цената е по тарифата на шофьора за избрания маршрут.','Price uses the driver\'s tariff for the chosen route.')+'</p>';
  document.body.style.setProperty('--rh',card.offsetHeight+'px');
}
function choose(i){if(!R||i===R.sel)return;R.sel=i;F.buzz(8);render();draw();}

function reverse(p,my){
  fetch('https://photon.komoot.io/reverse?lat='+p.lat+'&lon='+p.lng+'&limit=1').then(function(r){return r.json();}).then(function(j){
    if(my!==seq||!R)return;var f=(j.features||[])[0];if(!f)return;var q=f.properties||{};
    var st=[q.street,q.housenumber].filter(Boolean).join(' '),name=q.name||st||q.district||q.city;
    if(!name)return;R.to.label=name+(q.name&&st?', '+st:'')+(q.city&&q.city!==name?', '+q.city:'');render();
  }).catch(function(){});
}
function routes(a,b,my){
  fetch('https://router.project-osrm.org/route/v1/driving/'+a.lng+','+a.lat+';'+b.lng+','+b.lat+'?alternatives=3&overview=full&geometries=geojson')
   .then(function(r){return r.json();}).then(function(j){
    if(my!==seq||!R)return;
    var rs=(j.routes||[]).slice(0,3);R.wait=false;R.routes=rs;
    if(rs.length){
      var f=0,s=0;rs.forEach(function(r,i){if(r.duration<rs[f].duration)f=i;if(r.distance<rs[s].distance)s=i;});
      R.fast=f;R.short=s;R.sel=f;
    }
    render();draw();fit();
  }).catch(function(){if(my!==seq||!R)return;R.wait=false;R.routes=[];render();});
}
function pick(ll){
  if(R&&R.view==='pick'&&history.state&&history.state.ftr===2){try{history.replaceState({ftr:1},'',location.href);}catch(e){}}
  var my=++seq;F.buzz([15,40,15]);
  if(pin)map.removeLayer(pin);
  pin=L.marker(ll,{icon:L.divIcon({className:'dpin',iconSize:[0,0],html:'<b></b><i></i>'}),interactive:false,zIndexOffset:900}).addTo(map);
  var from=F.me?{lat:F.me.lat,lng:F.me.lng,me:true}:{lat:F.C[0],lng:F.C[1],me:false};
  R={from:from,to:{lat:ll.lat,lng:ll.lng,label:ll.lat.toFixed(5)+', '+ll.lng.toFixed(5)},routes:[],sel:0,wait:true,view:'routes'};
  open();render();draw();
  reverse(ll,my);routes(from,ll,my);
  F.track&&F.track('route_pick');
}
function open(){
  card.classList.add('open');document.body.classList.add('rmode');
  if(!pushed){try{history.pushState({ftr:1},'',location.href);pushed=true;}catch(e){}}
}
function close(fromBack){
  seq++;card.classList.remove('open');document.body.classList.remove('rmode');
  lines.forEach(function(l){map.removeLayer(l);});lines=[];if(pin){map.removeLayer(pin);pin=null;}R=null;
  var was=pushed;pushed=false;
  if(was&&!fromBack&&history.state&&history.state.ftr)history.go(-history.state.ftr);
}
/* „Назад“: затваря картичката; ако е бил отворен панел над нея — затваря само панела */
addEventListener('popstate',function(){
  if(!R)return;
  var s=history.state&&history.state.ftr;
  if(!s){close(true);return;}
  if(s===1&&R.view==='pick'){R.view='routes';render();}
});

card.addEventListener('click',function(e){
  if(e.target.closest('.x')){close(false);return;}
  var b=e.target.closest('.rt');if(b){choose(+b.dataset.i);return;}
  if(!R)return;
  if(e.target.closest('[data-a="order"]')){
    R.view='pick';F.buzz(8);render();card.scrollTop=0;
    try{history.pushState({ftr:2},'',location.href);}catch(er){}
    return;
  }
  if(e.target.closest('[data-a="back"]')){if(history.state&&history.state.ftr===2)history.back();else{R.view='routes';render();}return;}
  var k=e.target.closest('.pk');
  if(k){
    var d=F.byId(k.dataset.id),r=R.routes[R.sel];if(!d)return;
    var pre={to:{lat:R.to.lat,lng:R.to.lng,label:R.to.label}};
    if(r&&R.from.me)pre.est={km:Math.round(r.distance/100)/10,min:Math.round(r.duration/60+3)};
    F.openOrder(d,pre);
  }
});

/* задържане (дълго докосване) или десен бутон върху картата */
map.on('contextmenu',function(e){if(document.body.classList.contains('popen'))return;pick(e.latlng);});
F.onTheme=function(){draw();};

/* веднъж: подсказка, че може да се задържи върху картата */
try{if(!localStorage.getItem('ft_hint_route')){setTimeout(function(){if(!document.body.classList.contains('popen')&&F.toast)F.toast(T('Задръж пръст върху картата, за да избереш докъде','Press and hold on the map to choose where to'));},3500);localStorage.setItem('ft_hint_route','1');}}catch(e){}
})(FT);
