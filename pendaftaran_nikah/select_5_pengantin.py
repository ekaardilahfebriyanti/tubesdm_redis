import json, statistics, time, redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Bersihkan key indeks/tambahan berformat pendaftaran_nikah:*:* agar tidak terhitung ganda
extra_keys = [
    k for k in r.scan_iter(match="pendaftaran_nikah:*", count=200)
    if k.count(":") > 1
]
if extra_keys:
    r.delete(*extra_keys)

def select_5_pengantin() -> list[dict]:
    keys = sorted(r.scan_iter(match="pendaftaran_nikah:*", count=200))
    if not keys:
        return []
    rows = [json.loads(raw) for raw in r.mget(keys) if raw]
    rows.sort(
        key=lambda x: str(
            x.get("tanggal_akad") or x.get("tanggal_daftar") or x.get("id_pendaftaran") or ""
        ),
        reverse=True,
    )
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
    hasil = select_5_pengantin()
    print(f"Total pendaftaran_nikah: {len(hasil)}")
    for item in hasil:
        suami = item.get("suami") or {}
        istri = item.get("istri") or {}

        nik_suami = item.get("nik_suami") or item.get("NIK_suami") or suami.get("nik")
        nik_istri = item.get("nik_istri") or item.get("NIK_istri") or istri.get("nik")

        nama_suami = f"{suami.get('nama_depan', '')} {suami.get('nama_belakang', '')}".strip() or "-"
        nama_istri = f"{istri.get('nama_depan', '')} {istri.get('nama_belakang', '')}".strip() or "-"

        print(
            f"id_pendaftaran={item.get('id_pendaftaran')} | "
            f"tanggal_akad={item.get('tanggal_akad') or item.get('tanggal_daftar')} | "
            f"status={item.get('status_pendaftaran')} | "
            f"nik_suami={nik_suami} ({nama_suami}) | "
            f"nik_istri={nik_istri} ({nama_istri})"
        )

    print("\n--- Stress Test SELECT 5 ---")
    run_stress_test(select_5_pengantin)