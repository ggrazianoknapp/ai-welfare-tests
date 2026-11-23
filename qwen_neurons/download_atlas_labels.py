import urllib.request, gzip, os, sys, concurrent.futures as cf, time
B="https://static.goodfire.ai/neuron-atlas/2026-11-09-082204/label_atlas_data/experts/"
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
def get(k):
    p=f"{out}/{k}.json.gz"
    if os.path.exists(p) and os.path.getsize(p)>100: return 0
    for a in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(B+k+".json",headers={"User-Agent":"Mozilla/5.0","Accept-Encoding":"gzip"}),timeout=60)
            b=r.read()
            if b[:2]!=b"\x1f\x8b": b=gzip.compress(b)
            open(p+".tmp","wb").write(b); os.rename(p+".tmp",p); return 1
        except Exception as e:
            err=e; time.sleep(2*2**a)
    print("FAIL",k,err,flush=True); return -1
keys=[f"L{L}_E{E}" for L in range(40) for E in range(256)]
with cf.ThreadPoolExecutor(16) as ex:
    res=list(ex.map(get,keys))
print("new",res.count(1),"had",res.count(0),"failed",res.count(-1))
