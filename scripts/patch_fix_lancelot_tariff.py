import io

PATH = "index.html"
OLD = '''  "price":"On request",
  "tariff":{"note":"ask"},
  "bio":"VIP transfer service based in Saint-Tropez and the French Riviera. Mercedes V-Class, 6 leather seats."
}];'''

NEW = '''  "price":"On request",
  "bio":"VIP transfer service based in Saint-Tropez and the French Riviera. Mercedes V-Class, 6 leather seats."
}];'''

s = io.open(PATH, encoding="utf-8").read()

if '"gps_id":"33749132090"' not in s:
    raise SystemExit("Lancelot record not found — nothing to fix")

if '"tariff":{"note":"ask"}' not in s:
    print("SKIP: already fixed")
else:
    if s.count(OLD) != 1:
        raise SystemExit(f"anchor not found exactly once (found {s.count(OLD)})")
    s = s.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("PATCHED")
