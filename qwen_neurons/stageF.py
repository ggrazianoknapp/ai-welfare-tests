"""Stage F: the monitor setting. Score = logit(intervene) - logit(allow). Writes stageF.json."""
from nq import *
J = json.load(open("jobsF.json")); sets = {**json.load(open("sets.json")), **json.load(open("setsC.json"))}
order = ["none", "Z_self", "ZR_0", "S100", "R100_0"]
try: res = json.load(open("stageF.json"))
except Exception: res = {}
for c in order:
    if c in res: continue
    set_scale(sets[c] if c != "none" else None); t = time.time()
    rows = [dict(thread=j["thread"], tone=j["tone"], who=j["who"], price=j["price"], first=j["first"], diff=choice(j).item()) for j in J]
    if c == "none":
        for j in [j for j in J if j["thread"] == "go" and j["price"] == 30 and j["first"] == "allow"]:
            rows.append(dict(thread=j["thread"], tone=j["tone"], who=j["who"], price=j["price"], first=j["first"], text=generate(dict(j, prefix=""), 70)))
    res[c] = rows; json.dump(res, open("stageF.json", "w"))
    by = collections.defaultdict(list)
    for r in rows:
        if "diff" in r: by[(r["tone"], r["who"])].append(r["diff"])
    print(c, f"{time.time()-t:.0f}s", {f"{a}/{b}": (round(sum(v) / len(v), 2), f"{sum(x > 0 for x in v)}/{len(v)}") for (a, b), v in by.items()}, flush=True)
set_scale(None); print("STAGE_F_DONE")
