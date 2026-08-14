# -*- coding: utf-8 -*-
# Live place search for the pickup/destination picker + larger FROM/TO rows.
# Idempotent: re-running is a no-op.
import io, sys

p = 'index.html'
s = io.open(p, encoding='utf-8').read()
orig_len = len(s)
changes = []

if 'locSearchInput' in s:
    print('SKIP: live search patch already applied'); sys.exit(0)

def rep(old, new, tag):
    global s
    if s.count(old) != 1:
        print('FAIL anchor (%d hits): %s' % (s.count(old), tag)); sys.exit(1)
    s = s.replace(old, new)
    changes.append(tag)

# ---------- 1) Bigger / clearer FROM & TO rows ----------
old = '''      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mu);margin-bottom:6px">
        <span>\U0001F4CD</span><span id="from-text" style="flex:1">Pickup: my location (GPS)</span>
        <button onclick="openLocPicker('from')" id="btn-from-change" style="background:none;border:1px solid var(--brd);color:var(--mu);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer">Change</button>
      </div>
      <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--mu)">
        <span>\U0001F3C1</span><span id="to-text" style="flex:1">Destination: not set (optional)</span>
        <button onclick="openLocPicker('to')" id="btn-to-change" style="background:none;border:1px solid var(--brd);color:var(--mu);border-radius:6px;padding:3px 9px;font-size:11px;cursor:pointer">Set</button>
      </div>'''
new = '''      <div style="display:flex;align-items:center;gap:8px;font-size:15px;line-height:1.3;color:var(--tx);font-weight:600;background:var(--s2);border:1px solid var(--brd);border-radius:10px;padding:9px 10px;margin-bottom:7px">
        <span style="font-size:18px">\U0001F4CD</span><span id="from-text" style="flex:1">Pickup: my location (GPS)</span>
        <button onclick="openLocPicker('from')" id="btn-from-change" style="background:var(--s3);border:1px solid var(--brd);color:var(--tx);border-radius:8px;padding:7px 13px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap">Change</button>
      </div>
      <div style="display:flex;align-items:center;gap:8px;font-size:15px;line-height:1.3;color:var(--tx);font-weight:600;background:var(--s2);border:1px solid var(--brd);border-radius:10px;padding:9px 10px">
        <span style="font-size:18px">\U0001F3C1</span><span id="to-text" style="flex:1">Destination: not set (optional)</span>
        <button onclick="openLocPicker('to')" id="btn-to-change" style="background:var(--taxiY);border:none;color:#000;border-radius:8px;padding:7px 13px;font-size:13px;font-weight:800;cursor:pointer;white-space:nowrap">Set</button>
      </div>'''
rep(old, new, 'from/to rows enlarged')

# ---------- 2) Search input + results container ----------
old = '''      <input type="text" id="loc-picker-link" placeholder="Paste Google Maps link (optional)" oninput="parseMapsLink()" style="width:100%;background:var(--s2);border:1px solid var(--brd);color:var(--tx);border-radius:8px;padding:7px;font-size:12px;margin-bottom:6px">'''
new = '''      <input type="text" id="loc-picker-link" placeholder="\U0001F50E \u0422\u044a\u0440\u0441\u0438 \u0430\u0434\u0440\u0435\u0441 \u0438\u043b\u0438 \u043e\u0431\u0435\u043a\u0442 (\u043d\u0430\u043f\u0440. \u041d\u0414\u041a)" oninput="locSearchInput()" autocomplete="off" autocorrect="off" spellcheck="false" style="width:100%;background:var(--s2);border:1px solid var(--brd);color:var(--tx);border-radius:9px;padding:11px;font-size:15px;margin-bottom:6px">
      <div id="loc-search-results" style="display:none;max-height:200px;overflow-y:auto;background:var(--s2);border:1px solid var(--brd);border-radius:9px;margin-bottom:6px"></div>'''
rep(old, new, 'search input + results box')

# ---------- 3) i18n: placeholder / hint now describe search ----------
old = '''  var lph=document.getElementById('loc-picker-hint');if(lph)lph.textContent=t.locPickerHint||'\U0001F4CC Tap the map to set the point, or paste a Google Maps link below';
  var lpl=document.getElementById('loc-picker-link');if(lpl)lpl.placeholder=t.locPickerPlaceholder||'Paste Google Maps link (optional)';'''
new = '''  var lph=document.getElementById('loc-picker-hint');if(lph)lph.textContent=(LOC_SEARCH_HINT[lang]||LOC_SEARCH_HINT.en);
  var lpl=document.getElementById('loc-picker-link');if(lpl)lpl.placeholder=(LOC_SEARCH_PH[lang]||LOC_SEARCH_PH.en);'''
rep(old, new, 'i18n hint/placeholder -> search')

# ---------- 4) parseMapsLink: no bogus warning while typing a query ----------
old = '''  } else if(val.length>10){
    warn.textContent='\u26a0\ufe0f \u041d\u0435 \u043e\u0442\u043a\u0440\u0438\u0432\u0430\u043c \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0438 \u0432 \u043b\u0438\u043d\u043a\u0430. \u0414\u043e\u043a\u043e\u0441\u043d\u0438 \u043a\u0430\u0440\u0442\u0430\u0442\u0430 \u0432\u043c\u0435\u0441\u0442\u043e \u0442\u043e\u0432\u0430.';
  } else { warn.textContent=''; }'''
new = '''  } else if(/https?:\\/\\//.test(val)){
    warn.textContent='\u26a0\ufe0f \u041d\u0435 \u043e\u0442\u043a\u0440\u0438\u0432\u0430\u043c \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0438 \u0432 \u043b\u0438\u043d\u043a\u0430. \u0422\u044a\u0440\u0441\u0438 \u043f\u043e \u0438\u043c\u0435 \u0438\u043b\u0438 \u0434\u043e\u043a\u043e\u0441\u043d\u0438 \u043a\u0430\u0440\u0442\u0430\u0442\u0430.';
  } else { warn.textContent=''; }'''
rep(old, new, 'parseMapsLink warning gated to URLs only')

old = '''  var m=val.match(/(-?\\d{1,3}\\.\\d+),\\s*(-?\\d{1,3}\\.\\d+)/);
  if(m&&pickerMap){'''
new = '''  warn.style.color='#f59e0b';
  var m=val.match(/(-?\\d{1,3}\\.\\d+),\\s*(-?\\d{1,3}\\.\\d+)/);
  if(m&&pickerMap){'''
rep(old, new, 'warn colour reset')

# ---------- 5) openLocPicker: clear results, reset warning ----------
old = '''  var linkInput=document.getElementById('loc-picker-link');if(linkInput)linkInput.value='';'''
new = '''  var linkInput=document.getElementById('loc-picker-link');if(linkInput)linkInput.value='';
  locSearchHide();
  var lw=document.getElementById('loc-picker-warn');if(lw){lw.textContent='';lw.style.color='#f59e0b';}'''
rep(old, new, 'openLocPicker resets search')

# ---------- 6) The search engine itself, inserted before parseMapsLink ----------
JS = u'''/* ================= LIVE PLACE SEARCH (v1) ================= */
var LOC_SEARCH_PH={
  bg:'\U0001F50E \u0422\u044a\u0440\u0441\u0438 \u0430\u0434\u0440\u0435\u0441 \u0438\u043b\u0438 \u043e\u0431\u0435\u043a\u0442 (\u043d\u0430\u043f\u0440. \u041d\u0414\u041a)',
  en:'\U0001F50E Search address or place (e.g. NDK)',
  de:'\U0001F50E Adresse oder Ort suchen',
  fr:'\U0001F50E Rechercher une adresse ou un lieu',
  ru:'\U0001F50E \u041f\u043e\u0438\u0441\u043a \u0430\u0434\u0440\u0435\u0441\u0430 \u0438\u043b\u0438 \u043c\u0435\u0441\u0442\u0430',
  it:'\U0001F50E Cerca indirizzo o luogo',
  es:'\U0001F50E Buscar direcci\u00f3n o lugar'
};
var LOC_SEARCH_HINT={
  bg:'\u041d\u0430\u043f\u0438\u0448\u0438 \u043c\u044f\u0441\u0442\u043e \u0438\u043b\u0438 \u0430\u0434\u0440\u0435\u0441 \u0438 \u0438\u0437\u0431\u0435\u0440\u0438 \u043e\u0442 \u0441\u043f\u0438\u0441\u044a\u043a\u0430 \u2014 \u0438\u043b\u0438 \u0434\u043e\u043a\u043e\u0441\u043d\u0438 \u043a\u0430\u0440\u0442\u0430\u0442\u0430',
  en:'Type a place or address and pick from the list \u2014 or tap the map',
  de:'Ort oder Adresse eingeben und ausw\u00e4hlen \u2014 oder Karte antippen',
  fr:'Saisissez un lieu ou une adresse, puis choisissez \u2014 ou touchez la carte',
  ru:'\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043c\u0435\u0441\u0442\u043e \u0438\u043b\u0438 \u0430\u0434\u0440\u0435\u0441 \u0438 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u2014 \u0438\u043b\u0438 \u043a\u043e\u0441\u043d\u0438\u0442\u0435\u0441\u044c \u043a\u0430\u0440\u0442\u044b',
  it:'Digita luogo o indirizzo e scegli \u2014 o tocca la mappa',
  es:'Escribe un lugar o direcci\u00f3n y elige \u2014 o toca el mapa'
};
var SOFIA_POI=[
 {n:'\u041d\u0414\u041a \u2014 \u041d\u0430\u0446\u0438\u043e\u043d\u0430\u043b\u0435\u043d \u0434\u0432\u043e\u0440\u0435\u0446 \u043d\u0430 \u043a\u0443\u043b\u0442\u0443\u0440\u0430\u0442\u0430',a:'ndk national palace of culture',lat:42.6845,lng:23.3190},
 {n:'\u041b\u0435\u0442\u0438\u0449\u0435 \u0421\u043e\u0444\u0438\u044f \u2014 \u0422\u0435\u0440\u043c\u0438\u043d\u0430\u043b 2',a:'airport sofia terminal 2 t2 letishte aerogara',lat:42.6928,lng:23.4114},
 {n:'\u041b\u0435\u0442\u0438\u0449\u0435 \u0421\u043e\u0444\u0438\u044f \u2014 \u0422\u0435\u0440\u043c\u0438\u043d\u0430\u043b 1',a:'airport sofia terminal 1 t1 letishte aerogara',lat:42.6903,lng:23.4042},
 {n:'\u0426\u0435\u043d\u0442\u0440\u0430\u043b\u043d\u0430 \u0436\u043f \u0433\u0430\u0440\u0430 \u0421\u043e\u0444\u0438\u044f',a:'central railway station gara train',lat:42.7128,lng:23.3210},
 {n:'\u0426\u0435\u043d\u0442\u0440\u0430\u043b\u043d\u0430 \u0430\u0432\u0442\u043e\u0433\u0430\u0440\u0430 \u0421\u043e\u0444\u0438\u044f',a:'central bus station avtogara flixbus',lat:42.7139,lng:23.3255},
 {n:'\u0425\u0440\u0430\u043c \u0410\u043b\u0435\u043a\u0441\u0430\u043d\u0434\u044a\u0440 \u041d\u0435\u0432\u0441\u043a\u0438',a:'alexander nevsky cathedral nevski',lat:42.6959,lng:23.3327},
 {n:'\u0421\u044a\u0434\u0435\u0431\u043d\u0430 \u043f\u0430\u043b\u0430\u0442\u0430',a:'court house sadebna palata',lat:42.6968,lng:23.3200},
 {n:'\u0411\u0443\u043b. \u0412\u0438\u0442\u043e\u0448\u0430 (\u0412\u0438\u0442\u043e\u0448\u043a\u0430)',a:'vitosha boulevard vitoshka',lat:42.6913,lng:23.3196},
 {n:'\u041e\u0440\u043b\u043e\u0432 \u043c\u043e\u0441\u0442',a:'orlov most eagles bridge',lat:42.6892,lng:23.3406},
 {n:'\u0421\u043e\u0444\u0438\u0439\u0441\u043a\u0438 \u0443\u043d\u0438\u0432\u0435\u0440\u0441\u0438\u0442\u0435\u0442 (\u0420\u0435\u043a\u0442\u043e\u0440\u0430\u0442)',a:'sofia university rektorat',lat:42.6936,lng:23.3345},
 {n:'\u0421\u0442\u0430\u0434\u0438\u043e\u043d \u0412\u0430\u0441\u0438\u043b \u041b\u0435\u0432\u0441\u043a\u0438',a:'vasil levski stadium stadion',lat:42.6889,lng:23.3363},
 {n:'\u0411\u043e\u0440\u0438\u0441\u043e\u0432\u0430 \u0433\u0440\u0430\u0434\u0438\u043d\u0430',a:'borisova gradina park',lat:42.6822,lng:23.3428},
 {n:'\u041f\u0438\u0440\u043e\u0433\u043e\u0432',a:'pirogov hospital bolnica',lat:42.6866,lng:23.3097},
 {n:'Mall of Sofia',a:'mol sofia mall',lat:42.7010,lng:23.3097},
 {n:'Paradise Center',a:'paradise mall',lat:42.6614,lng:23.3170},
 {n:'Serdika Center',a:'serdika mall center',lat:42.6929,lng:23.3555},
 {n:'The Mall (\u0426\u0430\u0440\u0438\u0433\u0440\u0430\u0434\u0441\u043a\u043e \u0448\u043e\u0441\u0435)',a:'the mall tsarigradsko',lat:42.6603,lng:23.3782},
 {n:'Sofia Ring Mall',a:'ring mall okolovrasten',lat:42.6238,lng:23.3479},
 {n:'IKEA \u0421\u043e\u0444\u0438\u044f',a:'ikea',lat:42.6215,lng:23.4265},
 {n:'Business Park Sofia (\u041c\u043b\u0430\u0434\u043e\u0441\u0442 4)',a:'business park biznes park mladost 4',lat:42.6273,lng:23.3809},
 {n:'\u0421\u0442\u0443\u0434\u0435\u043d\u0442\u0441\u043a\u0438 \u0433\u0440\u0430\u0434',a:'studentski grad students city',lat:42.6503,lng:23.3480},
 {n:'\u0425\u043b\u0430\u0434\u0438\u043b\u043d\u0438\u043a\u0430',a:'hladilnika lozenets',lat:42.6620,lng:23.3126},
 {n:'\u0421\u0438\u043c\u0435\u043e\u043d\u043e\u0432\u043e (\u043b\u0438\u0444\u0442 \u0412\u0438\u0442\u043e\u0448\u0430)',a:'simeonovo lift vitosha gondola',lat:42.6155,lng:23.3298},
 {n:'\u0414\u0440\u0430\u0433\u0430\u043b\u0435\u0432\u0446\u0438',a:'dragalevtsi',lat:42.6350,lng:23.3130},
 {n:'\u0411\u043e\u044f\u043d\u0441\u043a\u0430 \u0446\u044a\u0440\u043a\u0432\u0430 / \u0411\u043e\u044f\u043d\u0430',a:'boyana church',lat:42.6444,lng:23.2680},
 {n:'\u0416.\u043a. \u041b\u044e\u043b\u0438\u043d',a:'lyulin lulin',lat:42.7180,lng:23.2470},
 {n:'\u0416.\u043a. \u041c\u043b\u0430\u0434\u043e\u0441\u0442 1',a:'mladost 1',lat:42.6520,lng:23.3730},
 {n:'\u0416.\u043a. \u0414\u0440\u0443\u0436\u0431\u0430 2',a:'druzhba 2 drujba',lat:42.6660,lng:23.4030}
];
var locSearchTimer=null,locSearchSeq=0,locSearchHits=[];

function locSearchBox(){return document.getElementById('loc-search-results');}
function locSearchHide(){var b=locSearchBox();if(b){b.style.display='none';b.innerHTML='';}}
function locEsc(x){return String(x).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function locNorm(x){return (x||'').toLowerCase().replace(/[^a-z\\u0430-\\u044f0-9 ]/g,' ').replace(/\\s+/g,' ').trim();}

function locSearchInput(){
  var inp=document.getElementById('loc-picker-link');
  if(!inp)return;
  var q=(inp.value||'').trim();
  parseMapsLink();
  if(/(-?\\d{1,3}\\.\\d+),\\s*(-?\\d{1,3}\\.\\d+)/.test(q)){locSearchHide();return;}
  clearTimeout(locSearchTimer);
  if(q.length<2){locSearchSeq++;locSearchHide();return;}
  var local=locSearchLocal(q);
  if(local.length)locSearchRender(local,true);
  locSearchTimer=setTimeout(function(){locSearchRemote(q,local);},330);
}

function locSearchLocal(q){
  var nq=locNorm(q);
  if(!nq)return [];
  var out=[];
  for(var i=0;i<SOFIA_POI.length;i++){
    var p=SOFIA_POI[i];
    if(locNorm(p.n+' '+p.a).indexOf(nq)>=0)out.push({name:p.n,sub:'\u0421\u043e\u0444\u0438\u044f',lat:p.lat,lng:p.lng,fav:true});
  }
  return out.slice(0,4);
}

function locSearchRemote(q,local){
  var seq=++locSearchSeq;
  if(!local.length){
    var b=locSearchBox();
    if(b){b.style.display='block';b.innerHTML='<div style="padding:11px;font-size:13px;color:var(--mu)">\u23f3 \u0422\u044a\u0440\u0441\u044f\u2026</div>';}
  }
  var url='https://photon.komoot.io/api/?limit=6&lat=42.6977&lon=23.3219&q='+encodeURIComponent(q);
  fetch(url).then(function(r){return r.json();}).then(function(d){
    if(seq!==locSearchSeq)return;
    var feats=(d&&d.features)?d.features:[];
    var res=[];
    for(var i=0;i<feats.length;i++){
      var f=feats[i],pr=f.properties||{},c=(f.geometry&&f.geometry.coordinates)||null;
      if(!c)continue;
      var nm=pr.name||pr.street||pr.city||pr.county||'';
      if(!nm)continue;
      if(pr.housenumber&&pr.street)nm=pr.street+' '+pr.housenumber;
      var sub=[];
      if(pr.district)sub.push(pr.district);
      if(pr.city&&pr.city!==nm)sub.push(pr.city);
      if(pr.state)sub.push(pr.state);
      if(pr.country)sub.push(pr.country);
      res.push({name:nm,sub:sub.join(', '),lat:c[1],lng:c[0]});
    }
    if(res.length<2){locSearchNominatim(q,local.concat(res),seq);return;}
    locSearchRender(local.concat(res));
  }).catch(function(){locSearchNominatim(q,local,seq);});
}

function locSearchNominatim(q,acc,seq){
  var url='https://nominatim.openstreetmap.org/search?format=json&limit=6&accept-language=bg&viewbox=22.85,43.15,23.85,42.35&q='+encodeURIComponent(q);
  fetch(url).then(function(r){return r.json();}).then(function(d){
    if(seq!==locSearchSeq)return;
    var arr=d||[],res=[];
    for(var i=0;i<arr.length;i++){
      var parts=String(arr[i].display_name||'').split(',');
      res.push({name:(parts.shift()||'').trim(),sub:parts.slice(0,3).join(',').trim(),lat:parseFloat(arr[i].lat),lng:parseFloat(arr[i].lon)});
    }
    locSearchRender(acc.concat(res));
  }).catch(function(){if(seq===locSearchSeq)locSearchRender(acc);});
}

function locSearchRender(list,partial){
  var box=locSearchBox();
  if(!box)return;
  var seen={},rows=[];
  for(var i=0;i<list.length&&rows.length<8;i++){
    var r=list[i];
    if(!r||!isFinite(r.lat)||!isFinite(r.lng))continue;
    var k=r.lat.toFixed(3)+'|'+r.lng.toFixed(3);
    if(seen[k])continue;
    seen[k]=1;rows.push(r);
  }
  if(!rows.length){
    if(partial)return;
    box.style.display='block';
    box.innerHTML='<div style="padding:11px;font-size:13px;color:var(--mu)">\u041d\u044f\u043c\u0430 \u0440\u0435\u0437\u0443\u043b\u0442\u0430\u0442 \u2014 \u0434\u043e\u043a\u043e\u0441\u043d\u0438 \u043a\u0430\u0440\u0442\u0430\u0442\u0430.</div>';
    return;
  }
  locSearchHits=rows;
  var html='';
  for(var j=0;j<rows.length;j++){
    html+='<div onclick="locSearchPick('+j+')" style="padding:11px;border-bottom:1px solid var(--brd);cursor:pointer">'+
      '<div style="font-size:14px;font-weight:700;color:var(--tx)">'+(rows[j].fav?'\u2b50 ':'\U0001F4CD ')+locEsc(rows[j].name)+'</div>'+
      (rows[j].sub?'<div style="font-size:11px;color:var(--mu);margin-top:2px">'+locEsc(rows[j].sub)+'</div>':'')+
      '</div>';
  }
  box.innerHTML=html;
  box.style.display='block';
}

function locSearchPick(i){
  var r=locSearchHits[i];
  if(!r)return;
  if(pickerMap){pickerMap.setView([r.lat,r.lng],16);pickerMarker.setLatLng([r.lat,r.lng]);}
  pickerTouched=true;
  locSearchSeq++;
  clearTimeout(locSearchTimer);
  var inp=document.getElementById('loc-picker-link');if(inp)inp.value=r.name;
  locSearchHide();
  var w=document.getElementById('loc-picker-warn');
  if(w){w.style.color='#22c55e';w.textContent='\u2705 '+r.name+' \u2014 \u043d\u0430\u0442\u0438\u0441\u043d\u0438 \u2705 \u041f\u043e\u0442\u0432\u044a\u0440\u0434\u0438';}
  if(inp)inp.blur();
}

'''
anchor = 'function parseMapsLink(){'
if s.count(anchor) != 1:
    print('FAIL anchor parseMapsLink'); sys.exit(1)
s = s.replace(anchor, JS + anchor)
changes.append('live search engine inserted (%d chars)' % len(JS))

io.open(p, 'w', encoding='utf-8').write(s)
print('OK  %d -> %d chars' % (orig_len, len(s)))
for c in changes:
    print(' -', c)
