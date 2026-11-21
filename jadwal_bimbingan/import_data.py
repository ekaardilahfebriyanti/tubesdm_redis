import json
from pathlib import Path
import redis

# 1. Arahkan path ke folder 'data' yang sejajar dengan folder 'jadwal_bimbingan'
SCRIPT_DIR = Path(__file__).resolve().parent          # .../jadwal_bimbingan
DATA_DIR = SCRIPT_DIR.parent / "data"        # .../data
file_jadwal = DATA_DIR / "jadwal_bimbingan.json"

# 2. Inisialisasi koneksi ke server Redis
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 3. Memuat data dari file JSON
with open(file_jadwal, "r", encoding="utf-8") as f:
    data_jadwal = json.load(f)

# 4. Pilih hanya 4 atribut yang dibutuhkan (proyeksi atribut)
atribut_tabel = ["id_jadwal_bimbingan", "tanggal_bimbingan", "waktu_bimbingan", "ruangan", "status_bimbingan", "nip_penyuluh"]

pipe = r.pipeline()
jumlah_disimpan = 0
id_sudah_ada = []

for item in data_jadwal:
    id_jadwal = item["id_jadwal_bimbingan"]
    redis_key = f"jadwal_bimbingan:{id_jadwal}"

    # Cek apakah ID sudah terdaftar di Redis
    if r.exists(redis_key):
        id_sudah_ada.append(id_jadwal)
        continue

    # Bentuk dokumen baru hanya dengan 4 atribut terpilih
    dokumen = {key: item[key] for key in atribut_tabel}

    # Simpan ke Redis dengan nx=True sebagai pengaman ganda
    pipe.set(redis_key, json.dumps(dokumen), nx=True)
    jumlah_disimpan += 1

# 5. Eksekusi seluruh perintah ke Redis
if jumlah_disimpan > 0:
    pipe.execute()

print(f"Berhasil menyimpan {jumlah_disimpan} data baru ke Redis.")
if id_sudah_ada:
    print(f"Dilewati ({len(id_sudah_ada)} ID sudah ada): {id_sudah_ada}")
