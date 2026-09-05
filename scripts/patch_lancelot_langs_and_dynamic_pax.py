import io, re

PATH = "index.html"
s = io.open(PATH, encoding="utf-8").read()
orig = s

# ── 1. Езици на Lancelot: добавяме bg и ru ────────────────────────────
OLD_LANGS = '"langs":["fr","en"]'
if OLD_LANGS in s:
    s = s.replace(OLD_LANGS, '"langs":["fr","en","bg","ru"]', 1)
    print("langs: PATCHED")
elif '"langs":["fr","en","bg","ru"]' in s:
    print("langs: already done")
else:
    raise SystemExit("langs anchor not found")

# ── 2. Lancelot: V-Class е 7+1, значи 7 пътници, не 6 ─────────────────
OLD_SEATS = '"gps_id":"33749132090"'
i = s.find(OLD_SEATS)
if i < 0:
    raise SystemExit("lancelot record not found")
seg_end = s.find('}]', i)
seg = s[i:seg_end]
if '"seats":6' in seg:
    s = s[:i] + seg.replace('"seats":6', '"seats":7', 1) + s[seg_end:]
    print("seats: 6 -> 7")
elif '"seats":7' in seg:
    print("seats: already 7")
else:
    raise SystemExit("lancelot seats field not found")

# ── 3. Пътници: опциите се строят от seats на шофьора ─────────────────
OLD_OPTS = ('<option value="2" id="opt-pax-2">1–2</option>\n'
            '        <option value="3" id="opt-pax-3">3</option>\n'
            '        <option value="4" id="opt-pax-4">4</option>')
NEW_OPTS = '<option value="2" id="opt-pax-2">1–2</option>'

if OLD_OPTS in s:
    s = s.replace(OLD_OPTS, NEW_OPTS, 1)
    print("pax markup: PATCHED")
elif s.count('id="opt-pax-3"') == 0:
    print("pax markup: already done")
else:
    raise SystemExit("pax option markup not matched")

# ── 4. Функцията, която строи опциите според местата в колата ─────────
HELPER = '''
/* Пътници според конкретната кола: 4-местна дава 1-2/3/4,
   V-Class със 7 места дава до 7. seats е в профила на шофьора. */
function buildPaxOptions(d){
  var sel=document.getElementById('order-pax');
  if(!sel)return;
  var t=T[lang]||T.en;
  var max=parseInt(d&&d.seats,10);
  if(!max||max<2)max=4;
  var keep=sel.value;
  sel.innerHTML='';
  var o=document.createElement('option');
  o.value='2';o.id='opt-pax-2';o.textContent=t.paxOpt2||'1\\u20132';
  sel.appendChild(o);
  for(var n=3;n<=max;n++){
    var x=document.createElement('option');
    x.value=String(n);x.id='opt-pax-'+n;x.textContent=String(n);
    sel.appendChild(x);
  }
  if(keep&&parseInt(keep,10)<=max)sel.value=keep;
}
'''

if 'function buildPaxOptions' not in s:
    anchor = 'function checkPaxWarning('
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("checkPaxWarning anchor not found")
    s = s[:i] + HELPER.lstrip('\n') + '\n' + s[i:]
    print("helper: ADDED")
else:
    print("helper: already there")

# ── 5. Викаме я при отваряне на профил ────────────────────────────────
m = re.search(r'function openMod\(([A-Za-z_$][\w$]*)\)\s*\{', s)
if not m:
    raise SystemExit("openMod not found")
if 'buildPaxOptions(' + m.group(1) + ')' not in s:
    ins = m.end()
    s = s[:ins] + '\n  buildPaxOptions(' + m.group(1) + ');' + s[ins:]
    print("openMod hook: ADDED")
else:
    print("openMod hook: already there")

if s == orig:
    print("NOTHING CHANGED")
else:
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("WRITTEN")
