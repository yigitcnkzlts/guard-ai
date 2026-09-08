import time
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
