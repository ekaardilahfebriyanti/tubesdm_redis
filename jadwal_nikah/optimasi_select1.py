import json, statistics, time, redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Buat key berakhiran status (jadwal_nikah:<id>:<status>) dari data yang ada
for k in r.scan_iter(match="jadwal_nikah:*", count=200):
    if k.count(":") == 1:
        doc = json.loads(r.get(k))
        r.set(f"{k}:{doc['status_pernikahan']}", json.dumps(doc))

def select_1_optimasi(status="selesai"):
    keys = list(r.scan_iter(match=f"jadwal_nikah:*:{status}", count=200))
    rows = [json.loads(x) for x in r.mget(keys) if x] if keys else []
    rows.sort(key=lambda x: str(x.get("tanggal_nikah") or ""), reverse=True)
    return rows

hasil = select_1_optimasi("selesai")
print(f"Total jadwal_nikah ('selesai'): {len(hasil)}")
for item in hasil:
    print(
        item.get("id_jadwal_nikah"),
        item.get("tanggal_nikah"),
        item.get("lokasi"),
        item.get("status_pernikahan"),
        item.get("nip_penghulu"),
    )

print("\n--- Stress Test Optimasi SELECT 1 ---")
for n in (1, 5, 10):
    ms = []
    for _ in range(n):
        t0 = time.perf_counter()
        res = select_1_optimasi("selesai")
        ms.append((time.perf_counter() - t0) * 1000)
    print(f"{n:2d}x | rows={len(res)} | avg={statistics.mean(ms):.2f} ms | total={sum(ms):.2f} ms")