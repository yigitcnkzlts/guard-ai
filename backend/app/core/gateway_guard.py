import time
import json
from types import SimpleNamespace
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, limit: int, window_seconds: int): self.limit=limit; self.window_seconds=window_seconds; self._hits: dict[str, deque[float]]=defaultdict(deque)
    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now; hits=self._hits[key]
        while hits and hits[0] <= now-self.window_seconds: hits.popleft()
        if len(hits) >= self.limit: return False
        hits.append(now); return True

class IdempotencyStore:
    def __init__(self): self._values: dict[str, tuple[float, object]]={}
    def get(self,key:str,now:float|None=None):
        now=time.monotonic() if now is None else now; item=self._values.get(key)
        if not item or item[0] <= now: self._values.pop(key,None); return None
        return item[1]
    def put(self,key:str,value:object,ttl_seconds:int=300,now:float|None=None)->None:
        now=time.monotonic() if now is None else now; self._values[key]=(now+ttl_seconds,value)

class RedisRateLimiter:
    def __init__(self,url:str,limit:int,window_seconds:int):
        from redis import Redis
        self.client=Redis.from_url(url,decode_responses=True); self.limit=limit; self.window_seconds=window_seconds
    def allow(self,key:str,now:float|None=None)->bool:
        bucket=int(time.time()//self.window_seconds); redis_key=f"guard:rate:{key}:{bucket}"
        count=self.client.incr(redis_key)
        if count==1:self.client.expire(redis_key,self.window_seconds+1)
        return count<=self.limit

class RedisIdempotencyStore:
    def __init__(self,url:str):
        from redis import Redis
        self.client=Redis.from_url(url,decode_responses=True)
    def get(self,key:str,now:float|None=None):
        raw=self.client.get(f"guard:idempotency:{key}")
        if raw is None:return None
        value=json.loads(raw); return SimpleNamespace(status_code=value["status_code"],payload=value["payload"])
    def put(self,key:str,value:object,ttl_seconds:int=300,now:float|None=None)->None:
        self.client.setex(f"guard:idempotency:{key}",ttl_seconds,json.dumps({"status_code":value.status_code,"payload":value.payload}))

def create_security_stores(redis_url:str|None,limit:int):
    if redis_url:return RedisRateLimiter(redis_url,limit,60),RedisIdempotencyStore(redis_url)
    return RateLimiter(limit,60),IdempotencyStore()
