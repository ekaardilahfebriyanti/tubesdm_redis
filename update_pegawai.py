from pathlib import Path
import json
import redis

BASE_DIR = Path(__file__).resolve().parent
FILE_PENDUDUK = BASE_DIR / "data" / "penduduk.json"
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

TARGET_NIK_PEGAWAI = {
    "3273074303990062",
    "3273074610710120",
    "3273075209970106",
    "3273075301740096",
    "3273075403960125",
    "3273075603880190",
    "3273072712710179",
    "3273072111860157",
    "3273072509850090",
    "3273073011700019",
    "3273070102810020",
    "3273070510830156",
    "3273070601890152",
    "3273070811880048",
    "3273072010870144",
}


def update_file_penduduk(path: str = FILE_PENDUDUK) -> int:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    diubah = 0
    for row in data:
        nik = str(row.get("nik", "")).strip()
        if nik in TARGET_NIK_PEGAWAI:
            row["pekerjaan"] = "PNS"
            diubah += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return diubah


def update_pekerjaan_pns_redis() -> int:
    keys = list(r.scan_iter(match="penduduk:*", count=100))
    if not keys:
        return 0

    raw_values = r.mget(keys)
    diubah = 0

    for key, raw in zip(keys, raw_values):
        if not raw:
            continue
        dok = json.loads(raw)
        nik = str(dok.get("nik", "")).strip()

        if nik in TARGET_NIK_PEGAWAI:
            dok["pekerjaan"] = "PNS"
            if r.set(key, json.dumps(dok, ensure_ascii=False), xx=True):
                diubah += 1

    return diubah


if __name__ == "__main__":
    jml_file = update_file_penduduk()
    jml_redis = update_pekerjaan_pns_redis()
    print(f"Diupdate di data/penduduk.json: {jml_file} | Diupdate di Redis: {jml_redis}")