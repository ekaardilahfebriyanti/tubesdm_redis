import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def delete_by_id(id_pendaftaran: int) -> bool:
    redis_key = f"pendaftaran_nikah:{id_pendaftaran}"
    jumlah_terhapus = r.delete(redis_key)
    return jumlah_terhapus > 0

# menghapus 1 data
if delete_by_id(105):
    print("Data berhasil dihapus.")
else:
    print("Data tidak ditemukan.")

# menghapus beberapa key sekaligus dalam satu perintah
r.delete("pendaftaran_nikah:101", "pendaftaran_nikah:102")