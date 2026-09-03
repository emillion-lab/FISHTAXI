import io

PATH = "index.html"
OLD = '''  "id":3,"founder":3,"gps_id":"33749132090","name":"Lancelot Transfers","name_bg":"Lancelot Transfers",
  "city":"saint-tropez","lat":43.2677,"lng":6.6407,'''

NEW = '''  "id":3,"founder":3,"gps_id":"33749132090","name":"Lancelot Transfers","name_bg":"Lancelot Transfers",
  "avatar":"img/lancelot_avatar.jpg",
  "photos":["img/lancelot_car_riviera.jpg","img/lancelot_car_chalet.jpg","img/lancelot_interior.jpg","img/lancelot_fleet.jpg","img/lancelot_helico.jpg"],
  "city":"saint-tropez","lat":43.2677,"lng":6.6407,'''

s = io.open(PATH, encoding="utf-8").read()

if '"avatar":"img/lancelot_avatar.jpg"' in s:
    print("SKIP: already patched")
else:
    if s.count(OLD) != 1:
        raise SystemExit(f"anchor not found exactly once (found {s.count(OLD)})")
    s = s.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("PATCHED")
