import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
pipe = r.pipeline()

# scan_iter mencari dan menelusuri daftar key di Redis berdasarkan pola tertentu

for redis_key in r.scan_iter("pendaftaran_nikah:*"):
    raw_data = r.get(redis_key)
    if not raw_data:
        continue

    dokumen = json.loads(raw_data)

    # Hapus nik_suami dan nik_istri dari level induk
    dokumen.pop("nik_suami", None)
    dokumen.pop("nik_istri", None)

    pipe.set(redis_key, json.dumps(dokumen))

pipe.execute()
print("Semua data pendaftaran_nikah berhasil dibersihkan.")