import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if a not in s and b in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

# езици само със знамена
sub('lib/app-core.js', "F.LN=LN;",
 "F.LN=LN;\nF.FLAG={bg:'🇧🇬',en:'🇬🇧',ru:'🇷🇺',de:'🇩🇪',fr:'🇫🇷',tr:'🇹🇷',it:'🇮🇹',es:'🇪🇸',cs:'🇨🇿',ar:'🇸🇦',zh:'🇨🇳',ro:'🇷🇴',el:'🇬🇷',pl:'🇵🇱',nl:'🇳🇱'};")
u = 'lib/app-ui.js'
sub(u, "var tags=(d.langs||[]).map(function(l){return l.toUpperCase();}).join(' · '),x=[];",
       "var tags=(d.langs||[]).map(function(l){return F.FLAG[l]||l.toUpperCase();}).join(' '),x=[];")
sub(u, "row('langs',(d.langs||[]).map(function(l){return F.LN[l]||l;}).join(', '))",
       "row('langs',(d.langs||[]).map(function(l){return F.FLAG[l]||F.LN[l]||l;}).join(' '))")
# „Само онлайн“ отпада
sub(u, "var FILTERS=[['on','fOn'],['en','fEn']", "var FILTERS=[['en','fEn']")

# цял екран: връща се след превключване между приложения, но не и след ръчно излизане
f = 'lib/app-fs.js'
sub(f, "var tried=false;document.addEventListener('pointerup'",
 "var tried=false,userLeft=false,exitTs=0,hideTs=0;\n"
 "document.addEventListener('fullscreenchange',function(){if(on())userLeft=false;else{exitTs=Date.now();userLeft=document.visibilityState==='visible';}});\n"
 "document.addEventListener('visibilitychange',function(){\n"
 "  if(document.visibilityState==='hidden'){hideTs=Date.now();return;}\n"
 "  if(on())return;\n"
 "  var sys=Math.abs(exitTs-hideTs)<2500||Date.now()-exitTs<1500;\n"
 "  if(!userLeft||sys){userLeft=false;tried=false;}\n"
 "});\n"
 "document.addEventListener('pointerup'")

s = io.open('index.html', encoding='utf-8').read()
for old, new in [('app-core.js?v=4', 'app-core.js?v=5'), ('app-ui.js?v=6', 'app-ui.js?v=7'), ('app-fs.js?v=3', 'app-fs.js?v=4')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)
