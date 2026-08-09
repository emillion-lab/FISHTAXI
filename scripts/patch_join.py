"""Довършва join.html: истинският телефон и по-честно показване на лиценза.

Две поправки:

1. Телефонът беше примерен.

2. Лицензът се показваше само когато има дата, а липсата се премълчаваше.
   Регистърът обаче не е пълен — около 2250 от 9456 коли нямат вписана
   валидност. Мълчанието изглежда като одобрение; сега липсата се казва
   изрично и заявката пак минава, но с бележка.

Освен това: изтекъл лиценз вече не блокира изпращането, а само предупреждава.
Регистърът се обновява веднъж месечно и може да изостава от действителността —
по-добре човек да пише и да се уточни, отколкото да го отрежем по стари данни.
"""
import io

src = io.open('join.html', encoding='utf-8').read()
count = 0

def rep(old, new):
    global src, count
    c = src.count(old)
    assert c == 1, 'MARKER x%d: %r' % (c, old[:70])
    src = src.replace(old, new); count += 1

rep("const TEL = '359888123456';            // ← сменѝ с истинския номер",
    "const TEL = '359889638230';")

rep("""      ${to?`<div class="row"><span class="k">Лиценз</span><span class="v">
        <span class="badge ${valid?'ok':'warn'}">${valid?'валиден до '+to:'изтекъл '+to}</span></span></div>`:''}
      <div class="known">🔍<div>Тези данни идват от публичния регистър.
        ${nd?`Фирмата има <b>${nd}</b> вписани шофьори.`:''}
        Заявки с несъответстващи данни не се обработват.</div></div>""",
"""      <div class="row"><span class="k">Лиценз</span><span class="v">${
        to ? `<span class="badge ${valid?'ok':'warn'}">${
               valid ? 'валиден до '+fmtDate(to) : 'изтекъл '+fmtDate(to)}</span>`
           : '<span class="badge warn">няма вписана дата</span>'}</span></div>
      <div class="known">🔍<div>Данните идват от публичния регистър на
        Автомобилна администрация${nd?`. Превозвачът има <b>${nd}</b> вписани шофьори`:''}.
        ${to && !valid
          ? '<br><b>Лицензът в регистъра е изтекъл.</b> Ако е подновен, напиши го в съобщението — регистърът се обновява веднъж месечно.'
          : !to
          ? '<br>За този автомобил няма вписана валидност. Ще я проверим ръчно.'
          : ''}</div></div>""")

rep("""function pick(v){
  picked = v;
  const [pl, mi, oi, yr, to, nd] = v;
  const valid = to ? new Date(to) > new Date() : null;""",
"""function fmtDate(s){
  const [y,m,d] = (s||'').split('-');
  return d ? `${+d}.${+m}.${y}` : s;
}
function pick(v){
  picked = v;
  const [pl, mi, oi, yr, to, nd] = v;
  const valid = to ? new Date(to) > new Date() : null;""")

# в съобщението да личи какво е видяно в регистъра
rep("""  const msg = `Заявка за fish.taxi\\n\\n`
    + `Име: ${nm}\\nТелефон: ${ph}\\n`
    + `Автомобил: ${pl} · ${REG.mods[mi]}${yr?' ('+yr+')':''}\\n`
    + `Превозвач: ${REG.ops[oi]}`;""",
"""  const to = picked[4];
  const lic = to ? (new Date(to) > new Date()
        ? 'валиден до ' + fmtDate(to) : 'изтекъл ' + fmtDate(to))
      : 'няма вписана дата';
  const msg = `Заявка за fish.taxi\\n\\n`
    + `Име: ${nm}\\nТелефон: ${ph}\\n`
    + `Автомобил: ${pl} · ${REG.mods[mi]}${yr?' ('+yr+')':''}\\n`
    + `Превозвач: ${REG.ops[oi]}\\n`
    + `Лиценз: ${lic}`;""")

io.open('join.html', 'w', encoding='utf-8').write(src)
print('PATCHED %d blocks OK' % count)
