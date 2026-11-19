import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def update_by_id(id_pendaftaran: int, data_perubahan: dict) -> bool:
    redis_key = f"pendaftaran_nikah:{id_pendaftaran}"

    # 1. Ambil data lama
    raw_data = r.get(redis_key)
    if not raw_data:
        return False  # Key tidak ditemukan

    # 2. Ubah field yang diinginkan
    dokumen = json.loads(raw_data)
    dokumen.update(data_perubahan)

    # 3. Simpan kembali (xx=True memastikan hanya menimpa key yang sudah ada)
    berhasil = r.set(redis_key, json.dumps(dokumen), xx=True)
    return bool(berhasil)

# Contoh penggunaan: mengubah status_pendaftaran dan tempat_akad pada ID 90
sukses = update_by_id(90, {
    "status_pendaftaran": "diterima",
    "tempat_akad": "Masjid Agung Al-Ukhuwah"
})
print("Status update:", sukses)