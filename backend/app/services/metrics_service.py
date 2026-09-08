from collections import Counter
from threading import Lock

_lock=Lock(); _requests=Counter(); _latency_total_ms=0.0

def observe(method:str,path:str,status:int,latency_ms:float)->None:
    global _latency_total_ms
    route=path if not path.startswith("/api/gateway") else "/api/gateway/*"
    with _lock: _requests[(method,route,status)]+=1; _latency_total_ms+=latency_ms

def snapshot()->dict:
    with _lock:
        total=sum(_requests.values())
        return {"requests_total":total,"average_latency_ms":round(_latency_total_ms/total,2) if total else 0.0,"series":[{"method":k[0],"path":k[1],"status":k[2],"count":v} for k,v in _requests.items()]}
