import io

PATH = "index.html"
OLD = '''  "bio":"Non-smoker. IT specialist. Calm driving. Music on request via YouTube. 540L trunk. Small pets welcome."
}];'''

NEW = '''  "bio":"Non-smoker. IT specialist. Calm driving. Music on request via YouTube. 540L trunk. Small pets welcome."
},{
  "id":3,"founder":3,"gps_id":"33749132090","name":"Lancelot Transfers","name_bg":"Lancelot Transfers",
  "city":"saint-tropez","lat":43.2677,"lng":6.6407,
  "car":"Mercedes V-Class","plate":"FV-231-QE",
  "car_type":"minivan","accel":9.0,"seats":6,
  "online":false,"rating":5.0,"reviews":0,
  "payment":["cash","terminal"],
  "langs":["fr","en"],
  "electric":false,"smoking":false,"nosmoker":true,
  "petfriendly":"ask","childok":true,
  "sport":false,"fast":false,"comfort":true,
  "minivan":true,"suv":false,"luxury":true,
  "ac":true,"music":true,"chalga":false,"nomusic":false,
  "silent_ok":true,"talk_ok":true,"calm_ok":true,
  "terminal":true,
  "music_pop":false,"music_chalga":false,"music_rock":false,"music_classical":false,"music_jazz":false,"music_electronic":false,"music_chillout":false,"music_lounge":false,
  "airport":true,"longdist":true,"night":"ask","business":true,"legroom":true,"panoroof":false,"streaming":false,"usb":true,"tinted":true,
  "wheelchair":"ask","verified":true,
  "areas":"Saint-Tropez — French Riviera, Côte d'Azur",
  "phone":"+33749132090",
  "price":"On request",
  "tariff":{"note":"ask"},
  "bio":"VIP transfer service based in Saint-Tropez and the French Riviera. Mercedes V-Class, 6 leather seats."
}];'''

s = io.open(PATH, encoding="utf-8").read()

if '"gps_id":"33749132090"' in s:
    print("SKIP: already patched")
else:
    if s.count(OLD) != 1:
        raise SystemExit(f"anchor not found exactly once (found {s.count(OLD)})")
    s = s.replace(OLD, NEW, 1)
    io.open(PATH, "w", encoding="utf-8").write(s)
    print("PATCHED")
