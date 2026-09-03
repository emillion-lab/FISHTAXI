import base64, glob, os, sys

"""
Сглобява бинарни файлове от base64 парчета.

Всяко изображение се качва като img/_b64/<име>.jpg.partNN (чист текст,
понеже MCP конекторът качва само текст). Тук ги събираме по ред,
декодираме и записваме истинския .jpg, после трием парчетата.

Идемпотентно: ако няма парчета, не прави нищо и излиза чисто.
"""

B64DIR = "img/_b64"
OUTDIR = "img"

if not os.path.isdir(B64DIR):
    print("няма парчета за сглобяване")
    sys.exit(0)

# групираме по име на целевия файл
groups = {}
for p in glob.glob(os.path.join(B64DIR, "*.part*")):
    base = os.path.basename(p)
    name, part = base.rsplit(".part", 1)
    groups.setdefault(name, []).append((int(part), p))

if not groups:
    print("няма парчета за сглобяване")
    sys.exit(0)

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
        raise SystemExit(f"{name}: невалиден base64 — {e}")

    if not blob.startswith(b"\xff\xd8\xff"):
        raise SystemExit(f"{name}: резултатът не е JPEG")
    if not blob.rstrip(b"\x00").endswith(b"\xff\xd9"):
        raise SystemExit(f"{name}: JPEG-ът е отрязан (липсва край на файла)")

    out = os.path.join(OUTDIR, name)
    with open(out, "wb") as f:
        f.write(blob)
    print(f"{name}: {len(parts)} парчета → {len(blob)//1024} KB")

    for _, p in parts:
        os.remove(p)

# махаме папката, ако е останала празна
try:
    os.rmdir(B64DIR)
except OSError:
    pass
print("готово")
