import json
from pathlib import Path
import statistics
import time
import redis

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
file_penduduk = DATA_DIR / "penduduk.json"

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

ATRIBUT_EMBED = ["nama_depan", "nama_belakang", "tanggal_lahir", "jenis_kelamin"]

FALLBACK_PENDUDUK = {
    "3273076501790216": {
        "nama_depan": "Byrle",
        "nama_belakang": "Driuzzi",
        "tanggal_lahir": "1971-04-29",
        "jenis_kelamin": "L",
    },
    "3273076501790217": {
        "nama_depan": "Kristo",
        "nama_belakang": "Ciubutaro",
        "tanggal_lahir": "1983-09-27",
        "jenis_kelamin": "P",
    },
}


def load_penduduk_index() -> dict[str, dict]:
    index = {nik: dict(data) for nik, data in FALLBACK_PENDUDUK.items()}
    if file_penduduk.exists():
        with open(file_penduduk, "r", encoding="utf-8") as f:
            data_penduduk = json.load(f)
        for p in data_penduduk:
            nik = str(p.get("nik") or p.get("NIK") or "").strip()
            if nik:
                doc = {k: p.get(k) for k in ATRIBUT_EMBED}
                index[nik] = doc
    return index


def build_dokumen_101(penduduk_by_nik: dict[str, dict]) -> dict:
    nik_suami = "3273076501790216"
    nik_istri = "3273076501790217"
    return {
        "id_pendaftaran": 101,
        "nik_suami": nik_suami,
        "nik_istri": nik_istri,
        "ayah": "Ahmad Santoso",
        "ibu": "Siti Aminah",
        "no_telepon": "081234567890",
        "tanggal_akad": "2026-10-23",
        "hari_akad": "Jumat",
        "jam_akad": "08:00:00",
        "tempat_akad": "KUA Kecamatan Sukajadi",
        "fotocopy_ktp": "KTP_3273076501790216.png",
        "fotocopy_akta_kelahiran": "akta_3273076501790216_3273076501790217.png",
        "fotocopy_kk": "KK_3273076501790216_3273076501790217.png",
        "foto": "foto_3273076501790216_3273076501790217.png",
        "N1_pengantar_nikah": "N1_3273076501790216_3273076501790217.pdf",
        "N2_permohonan_kehendak_nikah": "N2_3273076501790216_3273076501790217.pdf",
        "N3_permohonan_pencatatan_isbat": None,
        "tanggal_isbat": None,
        "N4_persetujuan_calon_pengantin": "N4_3273076501790216_3273076501790217.pdf",
        "N5_surat_izin_orang_tua": "N5_3273076501790216_3273076501790217.pdf",
        "N6_surat_keterangan_kematian": None,
        "N7_penolakan_kehendak_nikah_rujuk": None,
        "pembayaran_administrasi": 0,
        "pembayaran_akad": 0,
        "jalur_pendaftaran": "online",
        "status_pendaftaran": "belum_bayar",
        "suami": penduduk_by_nik.get(nik_suami),
        "istri": penduduk_by_nik.get(nik_istri),
    }


def insert_2_pendaftaran_101(penduduk_by_nik: dict[str, dict] | None = None) -> tuple[bool, dict]:
    index_penduduk = penduduk_by_nik if penduduk_by_nik is not None else load_penduduk_index()
    dokumen = build_dokumen_101(index_penduduk)
    key = f"pendaftaran_nikah:{dokumen['id_pendaftaran']}"
    r.delete(key)
    r.set(key, json.dumps(dokumen))
    return True, dokumen


def run_stress_test(fn, repeats=(1, 5, 10)) -> None:
    for n in repeats:
        durations_ms = []
        for _ in range(n):
            key = "pendaftaran_nikah:101"
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
    penduduk_index = load_penduduk_index()
    inserted, doc = insert_2_pendaftaran_101(penduduk_index)
    key = f"pendaftaran_nikah:{doc['id_pendaftaran']}"
    if inserted:
        print(f"Berhasil insert {key} dengan embedded suami & istri.")

    tersimpan = r.get(key)
    if tersimpan:
        parsed = json.loads(tersimpan)
        print(
            f"Preview -> id={parsed.get('id_pendaftaran')} | "
            f"suami={parsed.get('suami', {}).get('nama_depan')} {parsed.get('suami', {}).get('nama_belakang')} | "
            f"istri={parsed.get('istri', {}).get('nama_depan')} {parsed.get('istri', {}).get('nama_belakang')} | "
            f"status={parsed.get('status_pendaftaran')}"
        )

    print("\n--- Stress Test INSERT 2 ---")
    run_stress_test(lambda: insert_2_pendaftaran_101(penduduk_index))
    # Pastikan data ID 101 tetap ada setelah stress test
    insert_2_pendaftaran_101(penduduk_index)