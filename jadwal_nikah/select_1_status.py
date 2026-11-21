import json
import statistics
import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Hapus key berakhiran :selesai agar tidak terhitung ganda
keys_selesai = list(r.scan_iter(match="jadwal_nikah:*:selesai", count=200))
if keys_selesai:
    r.delete(*keys_selesai)

def select_1_status(status_pernikahan: str = "selesai") -> list[dict]:
    keys = sorted(r.scan_iter(match="jadwal_nikah:*", count=200))
    if not keys:
        return []
    target = str(status_pernikahan).strip().lower()
    rows = [
        doc for raw in r.mget(keys) if raw
        for doc in [json.loads(raw)]
        if str(doc.get("status_pernikahan", "")).strip().lower() == target
    ]
    rows.sort(key=lambda x: str(x.get("tanggal_nikah") or ""), reverse=True)
    return rows

def run_stress_test(fn, repeats=(1, 5, 10)) -> None:
    for n in repeats:
        durations_ms = []
        row_count = 0
        for _ in range(n):
            t0 = time.perf_counter()
            res = fn()
            durations_ms.append((time.perf_counter() - t0) * 1000)
            row_count = len(res)
        print(
            f"Iterasi {n:2d}x | rows={row_count:3d} | "
            f"avg={statistics.mean(durations_ms):6.2f} ms | "
            f"min={min(durations_ms):6.2f} ms | "
            f"max={max(durations_ms):6.2f} ms | "
            f"total={sum(durations_ms):7.2f} ms"
        )

if __name__ == "__main__":
    hasil = select_1_status("selesai")
    print(f"Total jadwal_nikah ('selesai'): {len(hasil)}")
    for item in hasil:
        print(
            item.get("id_jadwal_nikah"),
            item.get("tanggal_nikah"),
            item.get("lokasi"),
            item.get("status_pernikahan"),
            item.get("nip_penghulu"),
        )

    print("\n--- Stress Test SELECT 1 ---")
    run_stress_test(lambda: select_1_status("selesai"))