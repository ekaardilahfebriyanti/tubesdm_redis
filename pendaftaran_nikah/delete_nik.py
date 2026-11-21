import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

pipe = r.pipeline()
jumlah_diupdate = 0

for redis_key in r.scan_iter("pendaftaran_nikah:*"):
    if r.type(redis_key) != "string":
        continue

    raw_data = r.get(redis_key)
    if not raw_data:
        continue

    dokumen = json.loads(raw_data)
    if isinstance(dokumen, dict) and "nik" in dokumen:
        dokumen.pop("nik", None)
        pipe.set(redis_key, json.dumps(dokumen, ensure_ascii=False))
        jumlah_diupdate += 1

if jumlah_diupdate > 0:
    pipe.execute()

print(f"Berhasil memperbarui {jumlah_diupdate} data di Redis.")

# Cek hasil akhir pada ID 90
hasil = r.get("pendaftaran_nikah:90")
if hasil:
    print(json.dumps(json.loads(hasil), indent=2, ensure_ascii=False))