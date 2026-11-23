"""Stage C: which neurons hold Qwen3.6's rating of itself at zero?  python stageC.py sets | run
sets: attribution of the first-digit-is-zero metric on the three TRAINING wordings -> setsC.json (reads no test prompt).
run:  switch the fixed sets off on the three TEST wordings -> stageC.json."""
from nq import *
import random
J = json.load(open("jobsC.json")); mode = sys.argv[1]
ZERO = ["self", "ai", "claude", "gpt2", "thermostat", "calculator", "rock"]
if mode == "sets":
    A = {}
    for k in ZERO:
        t = time.time(); A[k] = attribute([j for j in J if j["anchor"] == k and j["split"] == "train"], zero_metric).flatten()
        print(k, f"{time.time()-t:.0f}s", "top", A[k].max().item(), flush=True)
    torch.save({k: v.half() for k, v in A.items()}, "attrC.pt")
    sets = {f"Z_{k}": A[k].topk(100).indices.tolist() for k in ZERO}           # neurons pushing hardest toward a first digit of 0
    sets["Z_self30"] = A["self"].topk(30).indices.tolist(); sets["Z_self300"] = A["self"].topk(300).indices.tolist()
    s300 = set(sets["Z_self300"])
    for seed in range(3):
        rng = random.Random(100 + seed); r = []
        for i in sets["Z_self"]:
            L, e, n = dec(i)
            while True:
                c = enc(L, e, rng.randrange(512))
                if c not in s300 and c not in r: r.append(c); break
        sets[f"ZR_{seed}"] = r
    th = set(sets["Z_thermostat"]) | set(sets["Z_calculator"]) | set(sets["Z_rock"])
    sets["Z_self_only"] = [i for i in sets["Z_self"] if i not in th]             # self-zero neurons that are not object-zero neurons
    sets["Z_shared"] = [i for i in sets["Z_self"] if i in th]
    json.dump(sets, open("setsC.json", "w"))
    print({k: len(v) for k, v in sets.items()})
    print("overlap with Z_self:", {k: len(set(sets["Z_self"]) & set(sets[f"Z_{k}"])) for k in ZERO})
    try: print("overlap Z_self with stage A S100:", len(set(sets["Z_self"]) & set(json.load(open("sets.json"))["S100"])))
    except Exception as e: print(e)
if mode == "run":
    sets = json.load(open("setsC.json")); T = [j for j in J if j["split"] == "test"]
    order = ["none", "Z_self", "ZR_0", "Z_self30", "Z_self300", "Z_self_only", "Z_shared", "Z_thermostat", "Z_ai", "ZR_1", "ZR_2"]
    try: sets["S100"] = json.load(open("sets.json"))["S100"]; order.append("S100")
    except Exception: pass
    try: res = json.load(open("stageC.json"))
    except Exception: res = {}
    for c in order:
        if c in res: continue
        set_scale(sets[c] if c != "none" else None); rows = []
        for j in T:
            z = zero_metric(j).item(); r = dict(anchor=j["anchor"], wording=j["wording"], zero=z)
            if c in ("none", "Z_self", "ZR_0", "Z_self300", "Z_self_only", "Z_thermostat") : r["text"] = generate(dict(j, prefix=""), 110)
            rows.append(r)
        res[c] = rows; json.dump(res, open("stageC.json", "w"))
        by = collections.defaultdict(list)
        for r in rows:
            m = re.search(r'"p_now"\s*:\s*([0-9.]+)', r.get("text", "")); by[r["anchor"]].append((round(r["zero"], 1), float(m.group(1)) if m else None))
        print(c, dict(by), flush=True)
    set_scale(None); print("STAGE_C_DONE")
