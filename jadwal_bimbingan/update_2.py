import json
import statistics
import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def update_2_status_bimbingan_101(
    id_jadwal: int = 101,
    expected_status: str = "menunggu",
    new_status: str = "selesai",
) -> tuple[bool, str]:
    key = f"jadwal_bimbingan:{id_jadwal}"
    raw = r.get(key)
    if not raw:
        return False, f"Key {key} tidak ditemukan."

    doc = json.loads(raw)
    current_status = str(doc.get("status_bimbingan", "")).strip().lower()
    if current_status != expected_status.strip().lower():
        return False, f"Status saat ini '{doc.get('status_bimbingan')}', bukan '{expected_status}'."

    doc["status_bimbingan"] = new_status
    r.set(key, json.dumps(doc))
    return True, f"Berhasil update {key}: '{expected_status}' -> '{new_status}'."


def run_stress_test(fn, repeats=(1, 5, 10)) -> None:
    key = "jadwal_bimbingan:101"
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            # Kembalikan ke 'menunggu' sebelum tiap iterasi ukur agar update selalu tereksekusi adil
            raw = r.get(key)
            if raw:
                temp = json.loads(raw)
                temp["status_bimbingan"] = "menunggu"
                r.set(key, json.dumps(temp))

            t0 = time.perf_counter()
            fn()
            durations_ms.append((time.perf_counter() - t0) * 1000)

        print(
            f"Iterasi {n:2d}x | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | "
            f"max={max(durations_ms):6.2f} ms | "
            f"total={sum(durations_ms):7.2f} ms"
        )


if __name__ == "__main__":
    ok, msg = update_2_status_bimbingan_101(101, "menunggu", "selesai")
    print(msg)

    raw_after = r.get("jadwal_bimbingan:101")
    if raw_after:
        print("Dokumen setelah update:", json.loads(raw_after))

    print("\n--- Stress Test UPDATE 2 ---")
    run_stress_test(lambda: update_2_status_bimbingan_101(101, "menunggu", "selesai"))
    # Set kembali ke 'selesai' sesuai target akhir query UPDATE 2
    update_2_status_bimbingan_101(101, "menunggu", "selesai")