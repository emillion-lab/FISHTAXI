import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if a not in s and b in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

# часове и минути
sub('lib/app-core.js', "F.LN=LN;",
 "F.LN=LN;\nF.dur=function(min){min=Math.round(min);var bg=F.lang==='bg';if(min<60)return min+' '+(bg?'мин':'min');var h=Math.floor(min/60),m=min%60;return h+' '+(bg?'ч':'h')+(m?' '+m+' '+(bg?'мин':'min'):'');};")
sub('lib/app-order.js', "' · ~'+O.est.min+' '+t('min')+(p?", "' · ~'+F.dur(O.est.min)+(p?")
sub('lib/app-order.js', "' km · ~'+O.est.min+' min'+(p?", "' km · ~'+F.dur(O.est.min).replace('ч','h')+(p?")
r = 'lib/app-route.js'
sub(r, "<b>'+Math.round(r.duration/60+3)+' '+T('мин','min')+'</b>", "<b>'+F.dur(r.duration/60+3)+'</b>")

# по-надеждни дълги маршрути: по-дълги таймаути, по-лека геометрия, три сървърни опита и допълнителни маршрути през междинна точка
s = io.open(r, encoding='utf-8').read()
i = s.index("var SRV=["); j = s.index("function pick(ll){")
new = r'''var SRV=['https://router.project-osrm.org/route/v1/driving/','https://routing.openstreetmap.de/routed-car/route/v1/driving/'];
function getJson(url,ms){
  return new Promise(function(ok,no){
    var done=false,ctl=window.AbortController?new AbortController():null,t=setTimeout(function(){if(done)return;done=true;try{ctl&&ctl.abort();}catch(e){}no(new Error('timeout'));},ms);
    fetch(url,ctl?{signal:ctl.signal}:{}).then(function(r){return r.json();}).then(function(j){if(done)return;done=true;clearTimeout(t);ok(j);},function(e){if(done)return;done=true;clearTimeout(t);no(e);});
  });
}
function hav(a,b){
  var d2r=Math.PI/180,dl=(b.lat-a.lat)*d2r,dn=(b.lng-a.lng)*d2r,
   h=Math.sin(dl/2)*Math.sin(dl/2)+Math.cos(a.lat*d2r)*Math.cos(b.lat*d2r)*Math.sin(dn/2)*Math.sin(dn/2);
  return 2*6371*Math.asin(Math.sqrt(h));
}
function fallback(a,b){
  var km=hav(a,b)*1.3;
  return [{distance:km*1000,duration:km/(km>40?70:30)*3600,approx:true,geometry:{type:'LineString',coordinates:[[a.lng,a.lat],[b.lng,b.lat]]}}];
}
function routes(a,b,my){
  var direct=hav(a,b),long=direct>40,ov=long?'simplified':'full',ms=long?11000:6500,
      ab=a.lng+','+a.lat+';'+b.lng+','+b.lat,tail='geometries=geojson&overview='+ov;
  var tries=[[SRV[0]+ab+'?alternatives=3&'+tail,ms],[SRV[1]+ab+'?alternatives=true&'+tail,ms],[SRV[0]+ab+'?alternatives=false&'+tail,ms+4000]];
  function fin(rs){
    if(my!==seq||!R)return;
    R.wait=false;R.routes=rs;
    if(rs.length){
      var f=0,s=0;rs.forEach(function(r,i){if(r.duration<rs[f].duration)f=i;if(r.distance<rs[s].distance)s=i;});
      R.fast=f;R.short=s;R.sel=f;
    }
    render();draw();fit();
  }
  /* ако сървърът върне по-малко от 3 пътя, търсим още през междинна точка встрани от правата линия */
  function more(rs,srv){
    if(rs.length>=3||my!==seq||!R){fin(rs);return;}
    var k=Math.cos((a.lat+b.lat)/2*Math.PI/180),mx=(a.lng+b.lng)/2,my2=(a.lat+b.lat)/2,
        dx=(b.lng-a.lng)*k,dy=b.lat-a.lat,len=Math.sqrt(dx*dx+dy*dy)||1,px=-dy/len,py=dx/len,off=len*(long?.16:.22),
        vs=[[mx+px*off/k,my2+py*off],[mx-px*off/k,my2-py*off]];
    Promise.all(vs.map(function(v){
      return getJson(srv+a.lng+','+a.lat+';'+v[0]+','+v[1]+';'+b.lng+','+b.lat+'?alternatives=false&'+tail,ms).then(function(j){return (j.routes||[])[0]||null;}).catch(function(){return null;});
    })).then(function(x){
      var best=rs[0].distance;
      x.forEach(function(r){
        if(!r||r.distance>best*1.5)return;
        if(rs.length<3&&rs.every(function(o){return Math.abs(o.distance-r.distance)/o.distance>.03;}))rs.push(r);
      });
      fin(rs);
    });
  }
  function go(n){
    if(my!==seq||!R)return;
    if(n>=tries.length){fin(fallback(a,b));return;}
    getJson(tries[n][0],tries[n][1]).then(function(j){
      var rs=(j.routes||[]).slice(0,3);
      if(rs.length)more(rs,n===1?SRV[1]:SRV[0]);else go(n+1);
    }).catch(function(){go(n+1);});
  }
  go(0);
}
'''
s = s[:i] + new + s[j:]
io.open(r, 'w', encoding='utf-8').write(s)
print('ok: routes rewritten')

s = io.open('index.html', encoding='utf-8').read()
for old, new in [('app-core.js?v=3', 'app-core.js?v=4'), ('app-order.js?v=4', 'app-order.js?v=5'), ('app-route.js?v=4', 'app-route.js?v=5')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)
