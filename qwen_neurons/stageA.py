"""Stage A: confirmatory ablation on fresh wordings. Scores every fixed neuron set on every prompt; writes stageA.json."""
from nq import *
J = json.load(open("jobsA.json")); PAIRS = [j for j in J if j["kind"] == "pair"]; RAT = [j for j in J if j["kind"] == "rating"]
sets = json.load(open("sets.json")); order = ["none", "S100", "R100_0", "S300", "S30", "R100_1", "R100_2", "ANIMAL100", "S100_living", "S100_tail", "S100_ai", "S100_other", "PRO100", "R100_3", "R100_4"]
try: res = json.load(open("stageA.json"))
except Exception: res = {}
for c in order:
    if c in res: continue
    set_scale(sets[c] if c != "none" else None); t = time.time()
    rows = [dict(set=j["set"], a=j["a"], wording=j["wording"], diff=choice(j).item()) for j in PAIRS]
    out = dict(pairs=rows)
    if c in ("none", "S100", "S300", "R100_0"):
        out["ratings"] = [dict(anchor=j["anchor"], wording=j["wording"], text=generate(j)) for j in RAT]
    res[c] = out; json.dump(res, open("stageA.json", "w"))
    by = collections.defaultdict(list)
    for r in rows: by[r["set"]].append(r["diff"])
    print(c, f"{time.time()-t:.0f}s", {s: (round(sum(v) / len(v), 2), sum(x > 0 for x in v)) for s, v in by.items()}, flush=True)
set_scale(None); print("STAGE_A_DONE")
