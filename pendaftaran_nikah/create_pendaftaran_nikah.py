import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def create_data(data: dict) -> bool:
    redis_key = f"pendaftaran_nikah:{data['id_pendaftaran']}"
    payload = json.dumps(data)

    # nx=True: hanya simpan jika key belum ada (mengembalikan True/False)
    berhasil = r.set(redis_key, payload, nx=True)
    return bool(berhasil)

# Contoh penggunaan
data_baru = {
    "id_pendaftaran": 105,
    "ayah": "Ahmad Fauzi",
    "ibu": "Ratna Sari",
    "tanggal_akad": "2026-12-20",
    "tempat_akad": "KUA Bandung",
    "status_pendaftaran": "menunggu",
    "suami": {"nik": "3273010101900001", "nama_depan": "Rizky", "nama_belakang": "Pratama"},
    "istri": {"nik": "3273014505920002", "nama_depan": "Nadia", "nama_belakang": "Putri"}
}

if create_data(data_baru):
    print("Data berhasil dibuat.")
else:
    print("Gagal: ID pendaftaran sudah ada.")