import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_all(pattern: str = "pendaftaran_nikah:*") -> list[dict]:
    # 1. Kumpulkan semua key yang cocok dengan pola
    keys = list(r.scan_iter(match=pattern, count=100))
    if not keys:
        return []

    # 2. Ambil seluruh value sekaligus dalam 1 batch
    raw_values = r.mget(keys)

    # 3. Konversi setiap string JSON menjadi dictionary
    hasil = [json.loads(val) for val in raw_values if val is not None]
    return hasil

# Contoh penggunaan
semua_data = get_all()
print(f"Total data ditemukan: {len(semua_data)}")