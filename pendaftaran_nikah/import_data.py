import json
from pathlib import Path
import redis

# 1. Arahkan path ke folder 'data' yang sejajar dengan folder 'pendaftaran_nikah'
SCRIPT_DIR = Path(__file__).resolve().parent          # Lokasi: .../pendaftaran_nikah
DATA_DIR = SCRIPT_DIR.parent / "data"        # Lokasi: .../data

file_penduduk = DATA_DIR / "penduduk.json"
file_pendaftaran = DATA_DIR / "pendaftaran_nikah.json"

# 2. Inisialisasi koneksi ke server Redis
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# 3. Memuat data dari kedua file JSON di folder data_import
with open(file_penduduk, "r", encoding="utf-8") as f:
    data_penduduk = json.load(f)

with open(file_pendaftaran, "r", encoding="utf-8") as f:
    data_pendaftaran = json.load(f)

# 4. Membuat indeks penduduk berdasarkan NIK (5 atribut)
atribut_embed = ["nik", "nama_depan", "nama_belakang", "tanggal_lahir", "jenis_kelamin"]
penduduk_by_nik = {
    p["nik"]: {key: p[key] for key in atribut_embed}
    for p in data_penduduk
}

# 5. Proses pengecekan ID, embedding, dan penyimpanan ke Redis menggunakan pipeline
pipe = r.pipeline()
jumlah_disimpan = 0
id_sudah_ada = []

for item in data_pendaftaran:
    id_pendaftaran = item["id_pendaftaran"]
    redis_key = f"pendaftaran_nikah:{id_pendaftaran}"

    # Cek apakah ID sudah terdaftar di Redis
    if r.exists(redis_key):
        id_sudah_ada.append(id_pendaftaran)
        continue

    dokumen = item.copy()

    # Embed data penduduk untuk suami & istri
    dokumen["suami"] = penduduk_by_nik.get(dokumen.get("nik_suami"))
    dokumen["istri"] = penduduk_by_nik.get(dokumen.get("nik_istri"))

    # Simpan ke Redis dengan nx=True sebagai pengaman ganda
    pipe.set(redis_key, json.dumps(dokumen), nx=True)
    jumlah_disimpan += 1

# 6. Eksekusi seluruh perintah ke Redis jika ada data baru
if jumlah_disimpan > 0:
    pipe.execute()

print(f"Berhasil menyimpan {jumlah_disimpan} data baru ke Redis.")
if id_sudah_ada:
    print(f"Dilewati ({len(id_sudah_ada)} ID sudah ada): {id_sudah_ada}")