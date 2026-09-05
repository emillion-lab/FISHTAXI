import io

PATH = "index.html"
OLD = '"avatar":"img/lancelot_avatar.jpg?v=2",'
NEW = '"avatar":"img/lancelot_avatar.jpg",'

s = io.open(PATH, encoding="utf-8").read()

if OLD not in s:
    print("SKIP: nothing to revert")
else:
    s = s.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("REVERTED")
