import io, json

# Добавя отпечатъка на ключа, с който Google Play подписва приложението (Play App Signing).
p = '.well-known/assetlinks.json'
NEW = '1F:D8:1E:AC:EF:39:BD:D8:AB:78:5B:E9:E6:1F:EB:08:B2:E3:68:26:7A:9F:17:A5:19:F4:EA:67:D7:18:9A:29'
d = json.load(io.open(p, encoding='utf-8'))
fp = d[0]['target']['sha256_cert_fingerprints']
if NEW in fp:
    print('already')
else:
    fp.append(NEW)
    io.open(p, 'w', encoding='utf-8').write(json.dumps(d, indent=2) + '\n')
    print('ok', len(fp))
