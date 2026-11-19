import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_by_id(id_jadwal_nikah: int) -> dict | None:
    redis_key = f"akta_nikah:{id_jadwal_nikah}"
    raw_data = r.get(redis_key)

    if raw_data:
        return json.loads(raw_data)
    return None

detail = get_by_id(100)
print(detail)