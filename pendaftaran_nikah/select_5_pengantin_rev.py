import json, statistics, time, redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
ZKEY = "pendaftaran_nikah:sort_akad"


def _skor_urut(doc: dict) -> float:
    # Mengubah "YYYY-MM-DD" menjadi angka agar bisa diurutkan dengan ZREVRANGE
    tanggal_akad = str(doc.get("tanggal_akad") or "")
    digits = "".join(ch for ch in tanggal_akad if ch.isdigit())
    return float(digits) if digits else float(doc.get("id_pendaftaran") or 0)


def bangun_indeks_akad(zkey: str = ZKEY) -> int:
    keys = [
        k
        for k in r.scan_iter(match="pendaftaran_nikah:*", count=200)
        if k != zkey and k.count(":") == 1
    ]
    r.delete(zkey)
    if not keys:
        return 0

    raws = r.mget(keys)
    mapping = {}
    for k, raw in zip(keys, raws):
        if raw:
            doc = json.loads(raw)
            mapping[k] = _skor_urut(doc)

    if mapping:
        r.zadd(zkey, mapping)
    return len(mapping)


def select_5_optimasi(zkey: str = ZKEY) -> list[dict]:
    keys = r.zrevrange(zkey, 0, -1)
    if not keys:
        return []
    raws = r.mget(keys)
    return [json.loads(raw) for raw in raws if raw]


def cetak_hasil(hasil: list[dict]) -> None:
    print(f"Total pendaftaran_nikah: {len(hasil)}")
    for item in hasil:
        suami = item.get("suami") or {}
        istri = item.get("istri") or {}

        nama_suami = f"{suami.get('nama_depan', '')} {suami.get('nama_belakang', '')}".strip() or "-"
        nama_istri = f"{istri.get('nama_depan', '')} {istri.get('nama_belakang', '')}".strip() or "-"

        print(
            f"id_pendaftaran={item.get('id_pendaftaran')} | "
            f"tanggal_akad={item.get('tanggal_akad') or item.get('tanggal_daftar')} | "
            f"status={item.get('status_pendaftaran')} | "
            f"nik_suami={item.get('nik_suami')} ({nama_suami}) | "
            f"nik_istri={item.get('nik_istri')} ({nama_istri})"
        )


def run_stress_test(fn, repeats=(1, 5, 10)) -> None:
    for n in repeats:
        ms = []
        row_count = 0
        for _ in range(n):
            t0 = time.perf_counter()
            res = fn()
            ms.append((time.perf_counter() - t0) * 1000)
            row_count = len(res)
        print(
            f"Iterasi {n:2d}x | rows={row_count:3d} | "
            f"avg={statistics.mean(ms):6.2f} ms | "
            f"min={min(ms):6.2f} ms | "
            f"max={max(ms):6.2f} ms | "
            f"total={sum(ms):7.2f} ms"
        )


if __name__ == "__main__":
    bangun_indeks_akad()
    hasil = select_5_optimasi()
    cetak_hasil(hasil)

    print("\n--- Stress Test Optimasi SELECT 5 ---")
    run_stress_test(select_5_optimasi)