import json
from pathlib import Path
import redis

# 1. Arahkan path ke folder 'data' yang sejajar dengan folder 'akta_nikah'
SCRIPT_DIR = Path(__file__).resolve().parent          # Lokasi: .../akta_nikah
DATA_DIR = SCRIPT_DIR.parent / "data"        # Lokasi: .../data

file_jadwal = DATA_DIR / "jadwal_nikah.json"
file_akta = DATA_DIR / "akta_nikah.json"

# 2. Inisialisasi koneksi ke server Redis
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 3. Memuat data dari folder import_data
with open(file_jadwal, "r", encoding="utf-8") as f:
    data_jadwal = json.load(f)

with open(file_akta, "r", encoding="utf-8") as f:
    data_akta = json.load(f)

# 4. Membuat indeks jadwal_nikah berdasarkan id_jadwal_nikah
atribut_embed = ["nama_wali", "tanggal_nikah", "lokasi", "status_pernikahan"]
jadwal_by_id = {
    j["id_jadwal_nikah"]: {key: j[key] for key in atribut_embed}
    for j in data_jadwal
}

# 5. Proses pengecekan ID, embedding, dan penyimpanan ke Redis menggunakan pipeline
pipe = r.pipeline()
jumlah_disimpan = 0
id_sudah_ada = []

for item in data_akta:
    id_jadwal = item["id_jadwal_nikah"]
    redis_key = f"akta_nikah:{id_jadwal}"

    # Cek apakah ID sudah terdaftar di Redis
    if r.exists(redis_key):
        id_sudah_ada.append(id_jadwal)
        continue

    dokumen = item.copy()

    # Embed data jadwal_nikah ke dalam dokumen akta_nikah
    dokumen["jadwal_nikah"] = jadwal_by_id.get(id_jadwal)

    # Simpan ke Redis dengan nx=True sebagai pengaman ganda
    pipe.set(redis_key, json.dumps(dokumen), nx=True)
    jumlah_disimpan += 1

# 6. Eksekusi seluruh perintah ke Redis jika ada data baru
if jumlah_disimpan > 0:
    pipe.execute()

print(f"Berhasil menyimpan {jumlah_disimpan} data baru ke Redis.")
if id_sudah_ada:
    print(f"Dilewati ({len(id_sudah_ada)} ID sudah ada): {id_sudah_ada}")