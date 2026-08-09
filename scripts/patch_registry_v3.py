"""Поправка: най-късната валидност на лиценза, не случайна.

Всяка кола има по няколко лиценза през годините — в регистъра се срещат
validTo от 2021 до 2026 за един и същи автомобил. Първата версия вземаше
което завари, затова коли с валиден лиценз излизаха "изтекъл 2024".

  validTo 2021: 37 · 2022: 117 · 2023: 6382 · 2024: 7711 · 2025: 7988 · 2026: 6105

Сега се взема max(validTo) по регистрационен номер. Ако най-късната дата е
в миналото, лицензът наистина е изтекъл и това се показва честно.
"""
import io

src = io.open('scripts/build_registry_index.py', encoding='utf-8').read()
count = 0

def rep(old, new):
    global src, count
    c = src.count(old)
    assert c == 1, 'MARKER x%d: %r' % (c, old[:70])
    src = src.replace(old, new); count += 1

rep("""            pl = (veh.get('registerNumber') or '').replace(' ', '').upper()
            if pl and lic.get('validTo'):
                valid[pl] = lic['validTo'][:10]""",
"""            pl = (veh.get('registerNumber') or '').replace(' ', '').upper()
            vt = (lic.get('validTo') or '')[:10]
            # една кола има по няколко лиценза през годините — взема се последният
            if pl and vt and vt > valid.get(pl, ''):
                valid[pl] = vt""")

io.open('scripts/build_registry_index.py', 'w', encoding='utf-8').write(src)
print('PATCHED %d blocks OK' % count)
