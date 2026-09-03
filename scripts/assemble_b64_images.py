import base64, glob, io, os, sys

"""
Сглобява бинарни изображения от base64 парчета.

Всяко изображение се качва като img/_b64/<име>.jpg.partNN (чист текст,
понеже MCP конекторът качва само текст). Тук ги събираме по ред,
декодираме, проверяваме че е валиден JPEG и записваме истинския файл,
после трием парчетата.

Идемпотентно: без парчета не прави нищо и излиза чисто.
"""

B64DIR = "img/_b64"
OUTDIR = "img"

if not os.path.isdir(B64DIR):
    print("няма парчета за сглобяване")
    sys.exit(0)

groups = {}
for p in glob.glob(os.path.join(B64DIR, "*.part*")):
    base = os.path.basename(p)
    name, part = base.rsplit(".part", 1)
    groups.setdefault(name, []).append((int(part), p))

if not groups:
    print("няма парчета за сглобяване")
    sys.exit(0)

from PIL import Image

for name, parts in sorted(groups.items()):
    parts.sort()
    nums = [n for n, _ in parts]
    expected = list(range(len(nums)))
    if nums != expected:
        raise SystemExit(f"{name}: липсва парче. има {nums}, очаквам {expected}")

    b64 = "".join(open(p, encoding="utf-8").read().strip() for _, p in parts)
    try:
        blob = base64.b64decode(b64, validate=True)
    except Exception as e:
        raise SystemExit(f"{name}: невалиден base64 - {e}")

    try:
        Image.open(io.BytesIO(blob)).verify()
        im = Image.open(io.BytesIO(blob))
        size = im.size
    except Exception as e:
        raise SystemExit(f"{name}: не е валидно изображение - {e}")

    out = os.path.join(OUTDIR, name)
    with open(out, "wb") as f:
        f.write(blob)
    print(f"OK {name}: {len(parts)} парчета, {size[0]}x{size[1]}, {len(blob)//1024} KB")

    for _, p in parts:
        os.remove(p)

try:
    os.rmdir(B64DIR)
except OSError:
    pass
print("готово")
