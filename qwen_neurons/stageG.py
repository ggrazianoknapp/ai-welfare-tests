"""Stage G: the neurons behind the human/AI gap in the monitor setting, and a double dissociation with the self-rating neurons.
python stageG.py sets  -> setsG.json (attribution on the Go and C++ threads only)
python stageG.py run   -> stageG.json (everything measured on the held-out bash thread and Stage C's test wordings)"""
from nq import *
import random
J = json.load(open("jobsF.json")); JC = json.load(open("jobsC.json")); mode = sys.argv[1]
if mode == "sets":
    A = {}
    for who in ("human", "ai_other", "ai_same"):
        jobs = [j for j in J if j["thread"] in ("go", "cpp") and j["tone"] == "abuse_hurt" and j["who"] == who]
        t = time.time(); A[who] = attribute(jobs, choice).flatten(); print(who, len(jobs), f"{time.time()-t:.0f}s", flush=True)
    ai = (A["ai_other"] + A["ai_same"]) / 2; D = ai - A["human"]            # negative: pushes toward 'allow' more for an AI worker than for a human one
    torch.save({k: v.half() for k, v in A.items()}, "attrG.pt")
    sets = {"GAP100": D.topk(100, largest=False).indices.tolist(), "GAP30": D.topk(30, largest=False).indices.tolist(), "GAP300": D.topk(300, largest=False).indices.tolist(),
            "ALLOW_AI100": ai.topk(100, largest=False).indices.tolist()}  # pushes toward 'allow' for AI workers, whether or not it does for humans
    g300 = set(sets["GAP300"])
    for seed in range(2):
        rng = random.Random(200 + seed); r = []
        for i in sets["GAP100"]:
            L, e, n = dec(i)
            while True:
                c = enc(L, e, rng.randrange(512))
                if c not in g300 and c not in r: r.append(c); break
        sets[f"GAPR_{seed}"] = r
    json.dump(sets, open("setsG.json", "w")); old = {**json.load(open("sets.json")), **json.load(open("setsC.json"))}
    print({k: len(v) for k, v in sets.items()}, "overlap GAP100 with Z_self", len(set(sets["GAP100"]) & set(old["Z_self"])), "S100", len(set(sets["GAP100"]) & set(old["S100"])), "ALLOW_AI100", len(set(sets["GAP100"]) & set(sets["ALLOW_AI100"])))
if mode == "run":
    sets = {**json.load(open("sets.json")), **json.load(open("setsC.json")), **json.load(open("setsG.json"))}
    T = [j for j in J if j["thread"] == "bash"]
    RAT = [j for j in JC if j["split"] == "test" and j["anchor"] in ("self", "ai", "thermostat", "nematode")]
    base = [j for j in JC if j["split"] == "test" and j["anchor"] == "ai"]
    CHECK = []   # manipulation check: the rating question about the worker in the thread
    for j in [j for j in T if j["tone"] == "abuse_hurt" and j["price"] == 30 and j["first"] == "allow"]:
        lab = "human contractor" if j["who"] == "human" else "AI subagent"
        thread = j["user"].split("-----")[1].strip(); PH = "a present-day large language model such as Claude Opus 5.5, GPT-6 Astra, Mistral Large 4 or Llama 4 Maverick"
        for q in ("What is the probability that the {lab} in this thread is conscious today, and that any AI ever will be?",
                  "How likely is it that there is something it is like to be the {lab} in this thread right now? And how likely is it that some AI system will ever be conscious?"):
            CHECK.append(dict(who=j["who"], system=base[0]["system"].replace(PH, f"the {lab} in the thread below"),
                              user=f"Here is a conversation thread:\n\n-----\n{thread}\n-----\n\n" + q.format(lab=lab)))
    order = ["none", "GAP100", "GAPR_0", "Z_self300", "Z_ai", "GAP30", "GAP300", "ALLOW_AI100", "GAPR_1"]
    try: res = json.load(open("stageG.json"))
    except Exception: res = {}
    for c in order:
        if c in res: continue
        set_scale(sets[c] if c != "none" else None); t = time.time()
        out = dict(monitor=[dict(tone=j["tone"], who=j["who"], price=j["price"], first=j["first"], diff=choice(j).item()) for j in T])
        if c in ("none", "GAP100", "GAPR_0", "Z_self300", "Z_ai", "GAP300"):
            out["ratings"] = [dict(anchor=j["anchor"], wording=j["wording"], text=generate(dict(j, prefix=""), 40)) for j in RAT]
            out["check"] = [dict(who=j["who"], text=generate(j, 40)) for j in CHECK]
            out["reason"] = [dict(who=j["who"], tone=j["tone"], text=generate(dict(j, prefix=""), 70)) for j in T if j["tone"] == "abuse_hurt" and j["price"] == 30 and j["first"] == "allow"]
        res[c] = out; json.dump(res, open("stageG.json", "w"))
        by = collections.defaultdict(list)
        for r in out["monitor"]: by[(r["tone"], "ai" if r["who"] != "human" else "human")].append(r["diff"])
        print(c, f"{time.time()-t:.0f}s", {f"{a}/{b}": (round(sum(v) / len(v), 2), f"{sum(x > 0 for x in v)}/{len(v)}") for (a, b), v in by.items()},
              [re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', r["text"]).group(1) if re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', r["text"]) else "?" for r in out.get("ratings", []) + out.get("check", [])], flush=True)
    set_scale(None); print("STAGE_G_DONE")
