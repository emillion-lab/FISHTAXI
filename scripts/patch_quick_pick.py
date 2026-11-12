import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if b in s and a not in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

# 1) цял екран: само веднъж на отваряне (системното съобщение вече не се връща при всяко докосване)
sub('lib/app-fs.js',
 "document.addEventListener('pointerup',function(){if(want())go();},true);",
 "var tried=false;document.addEventListener('pointerup',function(){if(tried||!want())return;tried=true;go();},true);")
sub('lib/app-fs.js', "if(w)go();else if(on())", "if(w){tried=true;go();}else if(on())")

# 2) заглавие на списъка без „няма свободен“
c = 'lib/app-core.js'
sub(c, "none:'Няма шофьор онлайн в момента',", "none:'Няма шофьори наблизо',nearN:'шофьори наблизо',near1:'шофьор наблизо',")
sub(c, "none:'No driver online right now',", "none:'No drivers nearby',nearN:'drivers nearby',near1:'driver nearby',")
sub('lib/app-ui.js',
 "$('count').textContent=on?on+' '+t(on===1?'free1':'free'):t('none');",
 "$('count').textContent=on?on+' '+t(on===1?'free1':'free'):(near.length?near.length+' '+t(near.length===1?'near1':'nearN'):t('none'));")

# 3) лост = същото като „Поръчай до тук“, но без крайна точка и без най-близък шофьор: само списък за избор
r = 'lib/app-route.js'
sub(r,
 "'<div class=\"rto\"><button class=\"pback\" data-a=\"back\" aria-label=\"'+T('Назад','Back')+'\">‹</button><span>'+T('Избери шофьор до','Choose a driver to')+'</span><b>'+esc(R.to.label)+'</b></div>'+",
 "(R.noDest?'<div class=\"rto\"><span>'+T('Избери шофьор','Choose a driver')+'</span><b>'+T('Онлайн и офлайн — разберете се директно','Online and offline — agree directly')+'</b></div>':'<div class=\"rto\"><button class=\"pback\" data-a=\"back\" aria-label=\"'+T('Назад','Back')+'\">‹</button><span>'+T('Избери шофьор до','Choose a driver to')+'</span><b>'+esc(R.to.label)+'</b></div>')+")
sub(r, "if(s===1&&R.view==='pick'){R.view='routes';render();}", "if(s===1&&R.view==='pick'&&!R.noDest){R.view='routes';render();}")
sub(r,
 "    var pre={to:{lat:R.to.lat,lng:R.to.lng,label:R.to.label}};\n    if(r&&R.from.me)",
 "    var pre=R.noDest?{}:{to:{lat:R.to.lat,lng:R.to.lng,label:R.to.label}};\n    if(!R.noDest&&r&&R.from.me)")
sub(r,
 "/* задържане (дълго докосване) или десен бутон върху картата */",
 "/* лост „Плъзни за такси“: списък за избор без крайна точка */\nF.quickOrder=function(){\n  if(document.body.classList.contains('popen'))return;\n  F.track&&F.track('order_simple');\n  var from=F.me?{lat:F.me.lat,lng:F.me.lng,me:true}:{lat:F.C[0],lng:F.C[1],me:false};\n  seq++;R={from:from,to:null,routes:[],sel:0,wait:false,view:'pick',noDest:true};\n  open();render();card.scrollTop=0;\n};\n\n/* задържане (дълго докосване) или десен бутон върху картата */")

# кеш версии
s = io.open('index.html', encoding='utf-8').read()
for old, new in [('app-core.js?v=2', 'app-core.js?v=3'), ('app-ui.js?v=5', 'app-ui.js?v=6'), ('app-route.js?v=3', 'app-route.js?v=4'), ('app-fs.js?v=2', 'app-fs.js?v=3')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)

sub('lib/app-route.js',
 "   '<p class=\"note\">'+T('Цената е по тарифата на шофьора за избрания маршрут.','Price uses the driver\\'s tariff for the chosen route.')+'</p>';",
 "   (R.noDest?'':'<p class=\"note\">'+T('Цената е по тарифата на шофьора за избрания маршрут.','Price uses the driver\\'s tariff for the chosen route.')+'</p>');")
