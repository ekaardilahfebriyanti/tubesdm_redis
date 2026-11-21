import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

pipe = r.pipeline()
jumlah_diupdate = 0

for key in r.scan_iter(match="pendaftaran_nikah:*"):
    raw_data = r.get(key)
    if not raw_data:
        continue

    dokumen = json.loads(raw_data)

    # Hapus key 'nik' di dalam objek suami & istri (aman jika bernilai None)
    if isinstance(dokumen.get("suami"), dict):
        dokumen["suami"].pop("nik", None)

    if isinstance(dokumen.get("istri"), dict):
        dokumen["istri"].pop("nik", None)

    pipe.set(key, json.dumps(dokumen), xx=True)
    jumlah_diupdate += 1

if jumlah_diupdate > 0:
    pipe.execute()

print(f"Berhasil memperbarui {jumlah_diupdate} data di Redis.")

# Cek hasil akhir pada ID 90
hasil = r.get("pendaftaran_nikah:90")
if hasil:
    print(json.dumps(json.loads(hasil), indent=2))