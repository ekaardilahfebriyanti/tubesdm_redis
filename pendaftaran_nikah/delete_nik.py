import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
pipe = r.pipeline()

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

pipe.execute()
print("Semua data pendaftaran_nikah berhasil dibersihkan.")