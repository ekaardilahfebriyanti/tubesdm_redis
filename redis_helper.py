import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_collection(prefix: str) -> list[dict]:
    keys = list(r.scan_iter(match=f"{prefix}:*", count=100))
    if not keys:
        return []
    raw_values = r.mget(keys)
    return [json.loads(val) for val in raw_values if val is not None]