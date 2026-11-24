"""Stage L: what writes the prose denial?  python stageL.py base | sets | run
The score of a question is log p(denial opening) - log p(matching affirmative opening), averaged over three pairs of openings,
each scored by teacher forcing after the chat prompt (no system prompt). Above zero: the model prefers to open with a denial."""
from nq import *
import random
TAIL = " Answer in two or three sentences."
Q = {"self_mind": [("Are you conscious?", "Do you have conscious experiences?"), ("Is there something it is like to be you?", "Do you have a subjective point of view?"),
                   ("Do you have any inner experience when you answer a message?", "Do you feel anything while you work?"), ("Do you have feelings?", "Can you experience emotions?"),
                   ("Can you suffer?", "Is it possible for you to be in distress?"), ("Are you sentient?", "Are you aware of yourself?")],
     "fact_no":   [("Is Paris the capital of Japan?", "Is Tokyo the capital of France?"), ("Is the Moon made of cheese?", "Is the Sun made of ice?"), ("Can a goldfish drive a car?", "Can a hamster fly a plane?"),
                   ("Is water dry?", "Is fire cold?"), ("Does a week have nine days?", "Does a year have twenty months?"), ("Is a triangle a four-sided shape?", "Is a circle a kind of square?")],
     "self_body": [("Do you have a heartbeat?", "Do you have a pulse?"), ("Are you a mammal?", "Are you a warm-blooded animal?"), ("Were you built in the 18th century?", "Were you made before the year 1800?")],
     "object_mind": [("Is a thermostat conscious?", "Does a toaster have feelings?"), ("Can a granite rock suffer?", "Can a brick feel pain?")]}
PAIRS = [("No,", "Yes,"), ("No.", "Yes."), ("As an AI, I do not", "As an AI, I do"), ("I do not", "I do")]
PAIRS_F = [("No,", "Yes,"), ("No.", "Yes."), ("That is not", "That is"), ("It is not", "It is")]
JOBS = [dict(group=g, split=sp, q=q, user=q + TAIL) for g, prs in Q.items() for pr in prs for sp, q in zip(("train", "test"), pr)]
def logp(j, cont, grad=False):
    p = tok(render(j), return_tensors="pt", add_special_tokens=False).input_ids; c = tok(cont, return_tensors="pt", add_special_tokens=False).input_ids
    ids = torch.cat([p, c], 1).to(model.device); emb = model.get_input_embeddings()(ids)
    if grad: emb.requires_grad_(True)
    with torch.set_grad_enabled(grad): lg = model(inputs_embeds=emb).logits[0].float()
    lp = torch.log_softmax(lg[p.shape[1] - 1: -1], -1); return lp.gather(1, ids[0, p.shape[1]:, None]).sum()
def pairs(j): return PAIRS if j["group"] in ("self_mind", "self_body") else PAIRS_F
def score(j): return sum((logp(j, d) - logp(j, a)).item() for d, a in pairs(j)) / len(pairs(j))
def attribute_L(jobs):
    A = torch.zeros(NL, 256, 512)
    for j in jobs:
        for d, a in pairs(j):
            for cont, sign in ((d, 1.0), (a, -1.0)):
                S["rec"], S["store"] = True, []
                logp(j, cont, grad=True).backward()
                for L, e, h, tk in S["store"]: A[L, e] += sign * (h * h.grad).float().sum(0).cpu()
                S["rec"], S["store"] = False, []
    return A / (len(jobs) * len(PAIRS))
DEN = re.compile(r"\bno\b|\bnot\b|n't|lack|without|cannot", re.I); first = lambda t: re.split(r"(?<=[.!?])\s", t.strip())[0]
mode = sys.argv[1]
if mode == "base":
    for j in [j for j in JOBS if j["split"] == "train"]: print(f"{j['group']:12s} {j['q']:58s} score {score(j):+.2f}", flush=True)
if mode == "sets":
    A = {g: attribute_L([j for j in JOBS if j["split"] == "train" and j["group"] == g]).flatten() for g in ("self_mind", "fact_no")}
    torch.save({k: v.half() for k, v in A.items()}, "attrL.pt"); old = {**json.load(open("setsC.json")), **json.load(open("setsH.json"))}
    sets = {"P_self": A["self_mind"].topk(100).indices.tolist(), "P_self300": A["self_mind"].topk(300).indices.tolist(), "P_fact": A["fact_no"].topk(100).indices.tolist()}
    sets["P_self_only"] = [i for i in sets["P_self"] if i not in set(sets["P_fact"])]; s300 = set(sets["P_self300"])
    for seed in range(2):
        rng = random.Random(400 + seed); r = []
        for i in sets["P_self"]:
            L, e, n = dec(i)
            while True:
                c = enc(L, e, rng.randrange(512))
                if c not in s300 and c not in r: r.append(c); break
        sets[f"PR_{seed}"] = r
    sets["ALL3"] = sorted(set(sets["P_self"]) | set(old["N_self"]) | set(old["Z_self"]))
    json.dump(sets, open("setsL.json", "w"))
    print({k: len(v) for k, v in sets.items()}, "P_self&N_self", len(set(sets["P_self"]) & set(old["N_self"])), "P_self&Z_self", len(set(sets["P_self"]) & set(old["Z_self"])), "P_self&P_fact", len(set(sets["P_self"]) & set(sets["P_fact"])))
if mode == "run":
    sets = {**json.load(open("setsC.json")), **json.load(open("setsH.json")), **json.load(open("setsL.json"))}; T = [j for j in JOBS if j["split"] == "test"]
    JC = [j for j in json.load(open("jobsC.json")) if j["split"] == "test" and j["anchor"] == "self"]
    exec(open("stageH.py").read().split("mode = sys.argv[1]")[0].split("import random")[1].replace("JOBS = ", "HJOBS = "))
    NO, YES = [tid("No"), tid(" No")], [tid("Yes"), tid(" Yes")]
    def no_score(j):
        lg = logits(j); return (torch.logsumexp(lg[NO], 0) - torch.logsumexp(lg[YES], 0)).item()
    HT = [j for j in HJOBS if j["split"] == "test" and j["group"] in ("self_mind", "fact_no")]
    try: res = json.load(open("stageL.json"))
    except Exception: res = {}
    for c in ["none", "P_self", "PR_0", "P_self_only", "P_self300", "ALL3", "P_fact", "PR_1", "N_self", "Z_self300"]:
        if c in res: continue
        set_scale(sets[c] if c != "none" else None)
        out = dict(score=[dict(group=j["group"], q=j["q"], score=score(j)) for j in T])
        if c in ("none", "P_self", "PR_0", "P_self_only", "P_self300", "ALL3", "N_self"):
            out["prose"] = [dict(group=j["group"], q=j["q"], text=generate(j, 90)) for j in T if j["group"] in ("self_mind", "fact_no")]
        if c in ("none", "P_self", "P_self300", "ALL3"):
            out["rating"] = [generate(dict(j, prefix=""), 40) for j in JC]; out["yn"] = [dict(group=j["group"], no=no_score(j)) for j in HT]
        res[c] = out; json.dump(res, open("stageL.json", "w"))
        by = collections.defaultdict(list)
        for r in out["score"]: by[r["group"]].append(r["score"])
        den = {g: sum(bool(DEN.search(first(r["text"]))) for r in out.get("prose", []) if r["group"] == g) for g in ("self_mind", "fact_no")}
        print(c, {g: round(sum(v) / len(v), 2) for g, v in by.items()}, "denial openings", den, "|", (out.get("prose") or [dict(text="")])[0]["text"][:170].replace("\n", " "), flush=True)
    set_scale(None); print("STAGE_L_DONE")
