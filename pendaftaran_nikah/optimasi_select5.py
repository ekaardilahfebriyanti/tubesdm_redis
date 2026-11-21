import json, statistics, time, redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def _skor_urut(doc: dict) -> float:
    raw = str(doc.get("tanggal_akad") or doc.get("tanggal_daftar") or doc.get("id_pendaftaran") or "0")
    digits = "".join(ch for ch in raw if ch.isdigit())
    return float(digits) if digits else 0.0

# Buat ZSET indeks urutan khusus dari key String asli pendaftaran_nikah:<id>
zkey = "pendaftaran_nikah:sort_akad"
pipe_z = r.pipeline()
has_zdata = False
for k in r.scan_iter(match="pendaftaran_nikah:*", count=200):
    if k != zkey and k.count(":") == 1 and r.type(k) == "string":
        raw = r.get(k)
        if raw:
            doc = json.loads(raw)
            pipe_z.zadd(zkey, {k: _skor_urut(doc)})
            has_zdata = True
if has_zdata:
    pipe_z.execute()

def select_5_optimasi() -> list[dict]:
    keys = r.zrevrange(zkey, 0, -1)
    if not keys:
        return []
    pipe = r.pipeline()
    for k in keys:
        pipe.get(k)
    raws = pipe.execute()
    return [json.loads(x) for x in raws if x]

hasil = select_5_optimasi()
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

print("\n--- Stress Test Optimasi SELECT 5 ---")
for n in (1, 5, 10):
    ms = []
    for _ in range(n):
        t0 = time.perf_counter()
        res = select_5_optimasi()
        ms.append((time.perf_counter() - t0) * 1000)
    print(f"{n:2d}x | rows={len(res)} | avg={statistics.mean(ms):.2f} ms | total={sum(ms):.2f} ms")