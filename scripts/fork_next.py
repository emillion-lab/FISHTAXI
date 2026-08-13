import re
import pathlib
import subprocess

SRC = 'index.html'
DST_DIR = pathlib.Path('next')
DST = DST_DIR / 'index.html'

s = open(SRC, encoding='utf-8').read()
assert '</head>' in s, 'няма </head>'

# 1) изолиран localStorage (същият origin, различен префикс)
s = s.replace('localStorage', '__nextLS')

# 2) service worker изключен в /next/
s = s.replace('navigator.serviceWorker', 'window.__nextNoSW')

shim = '''
<base href="/">
<meta name="robots" content="noindex">
<script>
(function(){
  var P = 'next:';
  window.__nextLS = {
    getItem:    function(k){ return localStorage.getItem(P + k); },
    setItem:    function(k, v){ return localStorage.setItem(P + k, v); },
    removeItem: function(k){ return localStorage.removeItem(P + k); },
    key:        function(){ return null; },
    length:     0,
    clear:      function(){
      Object.keys(localStorage)
        .filter(function(k){ return k.indexOf(P) === 0; })
        .forEach(function(k){ localStorage.removeItem(k); });
    }
  };
  window.__nextNoSW = {
    register:         function(){ return Promise.reject(new Error('SW off in /next/')); },
    ready:            new Promise(function(){}),
    getRegistrations: function(){ return Promise.resolve([]); },
    addEventListener: function(){}
  };
  if (navigator.serviceWorker && navigator.serviceWorker.getRegistrations) {
    navigator.serviceWorker.getRegistrations().then(function(rs){
      rs.forEach(function(r){ if (r.scope.indexOf('/next/') > -1) r.unregister(); });
    }).catch(function(){});
  }
})();
</script>
'''

s = s.replace('</head>', shim + '</head>', 1)

DST_DIR.mkdir(exist_ok=True)
DST.write_text(s, encoding='utf-8')
print('next/index.html: %d bytes' % len(s))

# --- проверки ---
scripts = re.findall(r'<script>(.*?)</script>', s, re.S)
main = max(scripts, key=len)
check_path = pathlib.Path('_check.js')
check_path.write_text(main, encoding='utf-8')
subprocess.run(['node', '--check', str(check_path)], check=True)
print('JS OK')

o = len(re.findall(r'<div', s))
c = len(re.findall(r'</div>', s))
assert o == c, f'div mismatch: {o} open vs {c} close'
print(f'div баланс ОК: {o}/{c}')

check_path.unlink()
