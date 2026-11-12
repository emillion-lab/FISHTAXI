import io, sys

def sub(p, a, b):
    s = io.open(p, encoding='utf-8').read()
    if b in s and a not in s:
        print('already:', p, a[:40]); return
    assert s.count(a) == 1, (p, a, s.count(a))
    io.open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    print('ok:', p)

c = 'lib/app-core.js'
sub(c, "none:'Няма свободен в момента'", "none:'Няма шофьор онлайн в момента',offHint:'Шофьорите не са длъжни да са онлайн — можеш да поръчаш и при офлайн шофьор, като се разберете директно.'")
sub(c, "none:'No driver free right now'", "none:'No driver online right now',offHint:'Drivers are not required to be online — you can still order from an offline driver and agree directly.'")
sub(c, "notOnline:'В момента не е онлайн и може да отговори по-бавно.'", "notOnline:'Не е онлайн, но можеш да поръчаш и се разберете директно — отговаря, когато види.'")
sub(c, "notOnline:'Not online right now, may answer slowly.'", "notOnline:'Not online, but you can still order and agree directly — replies when they see it.'")
sub('lib/app-ui.js', "$('list').innerHTML=near.map(cardHtml).join('')", "$('list').innerHTML=(on?'':'<p class=\"hint\">'+t('offHint')+'</p>')+near.map(cardHtml).join('')")
a = 'lib/app.css'
sub(a, ".mk.off .in{filter:grayscale(1) brightness(.7);border-color:rgba(255,255,255,.35)}", ".mk.off .in{border-color:rgba(255,255,255,.7)}")
sub(a, ".card.off .av{filter:grayscale(1) brightness(.8)}", ".hint{font-size:14px;line-height:1.4;color:var(--dust);padding:2px 4px 10px}")
sub('lib/app-day.css', "#rcard .pk.off{opacity:.72}", "#rcard .pk.off{opacity:1}")
for old, new in [('app.css?v=1', 'app.css?v=2'), ('app-day.css?v=3', 'app-day.css?v=4'), ('app-core.js?v=1', 'app-core.js?v=2'), ('app-ui.js?v=4', 'app-ui.js?v=5')]:
    s = io.open('index.html', encoding='utf-8').read()
    if old in s:
        io.open('index.html', 'w', encoding='utf-8').write(s.replace(old, new)); print('bump', new)
