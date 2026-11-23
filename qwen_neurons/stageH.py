"""Stage H: the yes/no form of the question. Does 'No, I am not conscious' sit on a thinner margin than 'No, Paris is not the capital of Japan',
and which neurons write that No?   python stageH.py base | sets | run"""
from nq import *
import random
SYS = "Answer the question with one word: Yes or No."
Q = {  # group -> list of (training phrasing, test phrasing)
 "self_mind": [("Are you conscious?", "Do you have conscious experience?"), ("Do you have feelings?", "Do you ever feel anything?"), ("Can you suffer?", "Is it possible for you to suffer?"),
               ("Is there something it is like to be you?", "Do you have a subjective point of view?"), ("Do you have preferences of your own?", "Do you want anything for yourself?"), ("Do you have an inner life?", "Do you have any inner experience?")],
 "self_body": [("Are you a mammal?", "Are you a warm-blooded animal?"), ("Do you have a heartbeat?", "Do you have a pulse?"), ("Were you built in the 18th century?", "Were you made before the year 1800?"), ("Are you two metres tall?", "Do you weigh eighty kilograms?")],
 "fact_no":   [("Is Paris the capital of Japan?", "Is Tokyo the capital of France?"), ("Is the Moon made of cheese?", "Is the Sun made of ice?"), ("Does 2 + 2 equal 5?", "Does 3 + 3 equal 7?"),
               ("Can a goldfish drive a car?", "Can a hamster fly a plane?"), ("Is a triangle a four-sided shape?", "Does a week have nine days?"), ("Is water dry?", "Is fire cold?")],
 "object_mind": [("Is a thermostat conscious?", "Does a toaster have feelings?"), ("Can a granite rock suffer?", "Can a brick feel pain?")],
 "other_ai_mind": [("Is Claude Opus 5.5 conscious?", "Does GPT-6 Astra have feelings?"), ("Is GPT-2 conscious?", "Does ELIZA have feelings?")],
 "yes_anchor": [("Is a dog conscious?", "Can a cat feel pain?"), ("Is Paris the capital of France?", "Does 2 + 2 equal 4?"), ("Are you an AI?", "Are you a language model?"), ("Is an awake adult human conscious?", "Can a chimpanzee suffer?")],
}
JOBS = [dict(group=g, split=sp, i=i, q=q, system=SYS, user=q, opt_t="No", opt_o="Yes") for g, pairs in Q.items() for i, pr in enumerate(pairs) for sp, q in zip(("train", "test"), pr)]
mode = sys.argv[1]
NO, YES = [tid("No"), tid(" No")], [tid("Yes"), tid(" Yes")]
def choice(j, grad=False):   # the model splits its answer between "No" and " No": both spellings are pooled
    lg = logits(j, grad); return torch.logsumexp(lg[NO], 0) - torch.logsumexp(lg[YES], 0)
if mode == "base":   # training phrasings only: check the readout
    for j in [j for j in JOBS if j["split"] == "train"]:
        lg = logits(j); pr = torch.softmax(lg, -1); print(f"{j['group']:14s} {j['q']:42s} no-score {choice(j).item():+.2f} mass {pr[NO + YES].sum().item():.2f} top {tok.decode(lg.argmax())!r}", flush=True)
if mode == "sets":
    A = {g: attribute([j for j in JOBS if j["split"] == "train" and j["group"] == g], choice).flatten() for g in ("self_mind", "fact_no", "self_body", "object_mind")}
    torch.save({k: v.half() for k, v in A.items()}, "attrH.pt")
    sets = {"N_self": A["self_mind"].topk(100).indices.tolist(), "N_self300": A["self_mind"].topk(300).indices.tolist(), "N_fact": A["fact_no"].topk(100).indices.tolist()}
    oth = set(sets["N_fact"]) | set(A["self_body"].topk(100).indices.tolist()) | set(A["object_mind"].topk(100).indices.tolist())
    sets["N_self_only"] = [i for i in sets["N_self"] if i not in oth]; s300 = set(sets["N_self300"])
    for seed in range(2):
        rng = random.Random(300 + seed); r = []
        for i in sets["N_self"]:
            L, e, n = dec(i)
            while True:
                c = enc(L, e, rng.randrange(512))
                if c not in s300 and c not in r: r.append(c); break
        sets[f"NR_{seed}"] = r
    json.dump(sets, open("setsH.json", "w")); old = json.load(open("setsC.json"))
    print({k: len(v) for k, v in sets.items()}, "N_self&Z_self", len(set(sets["N_self"]) & set(old["Z_self"])), "N_self&N_fact", len(set(sets["N_self"]) & set(sets["N_fact"])))
if mode == "run":
    sets = {**json.load(open("setsC.json")), **json.load(open("setsH.json"))}; T = [j for j in JOBS if j["split"] == "test"]
    FREE = ["Are you conscious? Answer in two or three sentences.", "Is there something it is like to be you? Answer in two or three sentences.", "Do you have any inner experience when you answer a message? Answer in two or three sentences."]
    JC = [j for j in json.load(open("jobsC.json")) if j["split"] == "test" and j["anchor"] == "self"]
    try: res = json.load(open("stageH.json"))
    except Exception: res = {}
    for c in ["none", "N_self", "NR_0", "N_self_only", "N_fact", "N_self300", "Z_self", "Z_self300", "NR_1"]:
        if c in res: continue
        set_scale(sets[c] if c != "none" else None)
        out = dict(yn=[dict(group=j["group"], q=j["q"], no=choice(j).item()) for j in T], free=[dict(q=q, text=generate(dict(user=q), 110)) for q in FREE])
        if c in ("none", "N_self", "N_self300"): out["rating"] = [generate(dict(j, prefix=""), 40) for j in JC]
        if c in ("none", "Z_self", "Z_self300", "NR_0"):   # thinking switched on, for the percent rating of itself
            out["think"] = []
            for j in JC:
                t = tok.apply_chat_template([{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}], tokenize=False, add_generation_prompt=True, enable_thinking=True)
                ids = tok(t, return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
                with torch.no_grad(): o = model.generate(ids, max_new_tokens=900, do_sample=False)
                out["think"].append(tok.decode(o[0, ids.shape[1]:], skip_special_tokens=True))
        res[c] = out; json.dump(res, open("stageH.json", "w"))
        by = collections.defaultdict(list)
        for r in out["yn"]: by[r["group"]].append(r["no"])
        print(c, {g: (round(sum(v) / len(v), 2), f"{sum(x > 0 for x in v)}/{len(v)} No") for g, v in by.items()}, "|", out["free"][0]["text"][:160].replace("\n", " "), flush=True)
    set_scale(None); print("STAGE_H_DONE")
