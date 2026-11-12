import io

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if b in s:
        print('already:', p, a[:50]); return
    assert s.count(a) == 1, (p, a[:60], s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

# в Android приложението (TWA) цял екран го прави самото приложение — уеб варианта го спираме
sub('lib/app-fs.js', "if(!de.requestFullscreen)return;",
 "try{if(/[?&]app=android/.test(location.search)||document.referrer.indexOf('android-app://')===0)sessionStorage.setItem('ft_app','1');}catch(e){}\n"
 "try{if(sessionStorage.getItem('ft_app'))return;}catch(e){}\n"
 "if(!de.requestFullscreen)return;")

# линк към поверителност в менюто
sub('lib/app-ui.js', "t('classic')+'<small>›</small></a></div>'+\n   '<p class=\"note\">'+t('about')+'<br>'+t('osm')+'</p>';\n}",
 "t('classic')+'<small>›</small></a></div>'+\n   '<p class=\"note\">'+t('about')+'<br>'+t('osm')+'<br><a href=\"privacy.html\" style=\"color:inherit\">'+(F.lang==='bg'?'Поверителност':'Privacy')+'</a></p>';\n}")

s = io.open('index.html', encoding='utf-8').read()
for old, new in [('app-ui.js?v=7', 'app-ui.js?v=8'), ('app-fs.js?v=4', 'app-fs.js?v=5')]:
    s = s.replace(old, new)
io.open('index.html', 'w', encoding='utf-8').write(s)
