import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if b in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

def app(p, marker, block):
    s = io.open(p, encoding='utf-8').read()
    if marker in s:
        print('already:', p, marker); return
    io.open(p, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + marker + '\n' + block + '\n')
    print('ok:', p, marker)

# заглавие без брой
sub('lib/app-core.js', "bg:{free:'свободни наблизо',", "bg:{nearT:'Шофьори наблизо',free:'свободни наблизо',")
sub('lib/app-core.js', "en:{free:'drivers free nearby',", "en:{nearT:'Drivers nearby',free:'drivers free nearby',")
sub('lib/app-ui.js',
 "$('count').textContent=on?on+' '+t(on===1?'free1':'free'):(near.length?near.length+' '+t(near.length===1?'near1':'nearN'):t('none'));",
 "$('count').textContent=arr.length?t('nearT'):t('none');")

# подредба само по разстояние
sub('lib/app-ui.js', "function order(a,b){return (b.online-a.online)||(F.km(a)-F.km(b));}",
 "function order(a,b){return F.km(a)-F.km(b);}")

# ориентировъчни минути за всички (и офлайн)
s = io.open('lib/app-ui.js', encoding='utf-8').read()
i = s.index("function etaHtml(d){")
j = s.index("F.etaHtml=etaHtml;")
if "~'+F.dur(F.mins(d))" not in s:
    s = s[:i] + "function etaHtml(d){\n  return '<span class=\"eta\" data-eta>~'+F.dur(F.mins(d))+'<small>'+F.kmTxt(F.km(d))+'</small></span>';\n}\n" + s[j:]
    io.open('lib/app-ui.js', 'w', encoding='utf-8').write(s)
    print('ok: etaHtml')

# карта: езици и екстри с иконки винаги видими
s = io.open('lib/app-ui.js', encoding='utf-8').read()
i = s.index("function cardHtml(d,i){")
j = s.index("var lastSig='';")
if "class=\"pl\"" not in s:
    new = (
"function cardHtml(d,i){\n"
"  var ex=(d.langs||[]).map(function(l){return F.FLAG[l]||l.toUpperCase();});\n"
"  if(d.electric)ex.push('⚡');if(d.childok===true)ex.push('👶');if(d.petfriendly===true)ex.push('🐾');\n"
"  if(d.terminal===true||(d.payment||[]).indexOf('terminal')>=0)ex.push('💳');if(d.seats>=6)ex.push('👥'+d.seats);\n"
"  return '<article class=\"card'+(d.online?'':' off')+(F.sel===d.id?' sel':'')+'\" data-id=\"'+d.id+'\" style=\"animation-delay:'+(i*45)+'ms\">'+\n"
"   '<button class=\"row\" aria-expanded=\"'+(F.sel===d.id)+'\"><img class=\"av\" src=\"'+esc(d.avatar||'favicon.png')+'\" alt=\"\">'+\n"
"   '<span class=\"who\"><b><i class=\"dot\"></i>'+esc(F.name(d))+'</b><span>'+esc(d.car)+'</span><span class=\"pl\"><span class=\"num\">'+esc(d.plate)+'</span><span class=\"ex\">'+ex.join(' ')+'</span></span></span>'+etaHtml(d)+'</button>'+\n"
"   '<div class=\"more\"><div>'+\n"
"   '<div class=\"acts\"><a class=\"btn\" href=\"tel:'+F.tel(d)+'\" data-tr=\"call\">'+t('call')+'</a><a class=\"btn\" href=\"viber://chat?number=%2B'+F.tel(d).slice(1)+'\" data-tr=\"viber\">Viber</a>'+\n"
"   '<button class=\"btn wide\" data-a=\"more\">'+t('details')+'</button><button class=\"btn wide go\" data-a=\"order\">'+t('orderAt')+' '+esc(F.first(d))+'</button></div></div></div></article>';\n"
"}\n")
    s = s[:i] + new + s[j:]
    io.open('lib/app-ui.js', 'w', encoding='utf-8').write(s)
    print('ok: cardHtml')

# лист: един жест нагоре отваря целия списък; докосване на заглавието го отваря/свива
sub('lib/app-ui.js', "if(Math.abs(e.clientY-sy)<5){snapTo((snapI+1)%3);return;}",
 "if(Math.abs(e.clientY-sy)<5){snapTo(snapI<2?2:1);return;}")
sub('lib/app-ui.js', "snapTo(best);}\n  g.addEventListener('pointerup',end)",
 "if(snapI===1&&e.clientY<sy-5&&best<2)best=2;snapTo(best);}\n  g.addEventListener('pointerup',end)")

app('lib/app.css', '/* v3.6 компактни карти */',
""".card .row{padding:10px 12px;gap:10px}
#list{gap:8px}
.av{width:46px;height:46px}
.who b{font-size:20px}
.who span{font-size:16px}
.who .pl{display:flex;align-items:center;gap:10px;margin-top:3px;flex-wrap:wrap}
.num,.who .num{font-size:14px;margin-top:0;padding:3px 7px 3px 15px}
.num::before{width:9px}
.who .ex{font-size:19px;line-height:1.2;letter-spacing:2px;color:inherit}
.eta{font-size:24px}
.eta small{font-size:14px}""")

s = io.open('index.html', encoding='utf-8').read()
for old, new in [('app-ui.js?v=8', 'app-ui.js?v=9'), ('app-core.js?v=5', 'app-core.js?v=6'), ('app.css?v=2', 'app.css?v=3')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)

# v3.6b: екстрите на отделен ред, далечните — само километри
sub('lib/app-ui.js',
 "return '<span class=\"eta\" data-eta>~'+F.dur(F.mins(d))+'<small>'+F.kmTxt(F.km(d))+'</small></span>';",
 "return F.near(d)?'<span class=\"eta\" data-eta>~'+F.dur(F.mins(d))+'<small>'+F.kmTxt(F.km(d))+'</small></span>':'<span class=\"eta far\" data-eta>'+F.kmTxt(F.km(d))+'</span>';")
sub('lib/app-ui.js',
 "<span class=\"num\">'+esc(d.plate)+'</span><span class=\"ex\">'+ex.join(' ')+'</span></span></span>'+etaHtml(d)+'</button>'+",
 "<span class=\"num\">'+esc(d.plate)+'</span></span></span>'+etaHtml(d)+'</button><div class=\"exr\">'+ex.join(' ')+'</div>'+")
app('lib/app.css', '/* v3.6b */',
""".exr{padding:0 12px 10px 68px;font-size:20px;line-height:1.25;letter-spacing:3px;margin-top:-4px}
.eta.far{font-size:16px;font-weight:600;color:var(--dust)}""")
