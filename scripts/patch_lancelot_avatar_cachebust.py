import io

PATH = "index.html"
OLD = '"avatar":"img/lancelot_avatar.jpg",'
NEW = '"avatar":"img/lancelot_avatar.jpg?v=2",'

s = io.open(PATH, encoding="utf-8").read()

if NEW in s:
    print("SKIP: already patched")
else:
    if s.count(OLD) != 1:
        raise SystemExit(f"anchor not found exactly once (found {s.count(OLD)})")
    s = s.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("PATCHED")
