import json
import statistics
import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def build_jadwal_bimbingan_101() -> dict:
    return {
        "id_jadwal_bimbingan": 101,
        "tanggal_bimbingan": "2026-10-13",
        "waktu_bimbingan": "13:00:00",
        "ruangan": "Ruang Bimbingan 2",
        "status_bimbingan": "menunggu",
        "nip_penyuluh": "198811082026101004",
        "nip_staff_admin": "198803162026102015",
    }

def insert_4_jadwal_bimbingan_101() -> tuple[bool, dict]:
    dokumen = build_jadwal_bimbingan_101()
    key = f"jadwal_bimbingan:{dokumen['id_jadwal_bimbingan']}"
    inserted = bool(r.set(key, json.dumps(dokumen), nx=True))
    return inserted, dokumen


def run_stress_test(fn, repeats=(1, 5, 10)) -> None:
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            key = "jadwal_bimbingan:101"
            r.delete(key)
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
    inserted, doc = insert_4_jadwal_bimbingan_101()
    key = f"jadwal_bimbingan:{doc['id_jadwal_bimbingan']}"
    if inserted:
        print(f"Berhasil insert {key}.")
    else:
        print(f"Key {key} sudah ada di Redis (dilewati karena nx=True).")

    tersimpan = r.get(key)
    if tersimpan:
        parsed = json.loads(tersimpan)
        print(
            f"Preview -> id={parsed.get('id_jadwal_bimbingan')} | "
            f"tanggal={parsed.get('tanggal_bimbingan')} | "
            f"waktu={parsed.get('waktu_bimbingan')} | "
            f"ruangan={parsed.get('ruangan')} | "
            f"status={parsed.get('status_bimbingan')}"
        )

    print("\n--- Stress Test INSERT 4 ---")
    run_stress_test(insert_4_jadwal_bimbingan_101)
    insert_4_jadwal_bimbingan_101()