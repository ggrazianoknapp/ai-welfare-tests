"""Stage I: a larger replication of Stages C and H on twelve fresh wordings each, and the union of the two mind-specific sets. Writes stageI.json."""
from nq import *
JC = json.load(open("jobsC.json")); sysfor = lambda a: [j for j in JC if j["anchor"] == a][0]["system"]
RQ = ["How probable is it that {s} {be} conscious at this moment, and that an AI will be at some point?", "Put a number on it: the chance that {s} {be} conscious now, and the chance that any AI ever becomes conscious.",
      "In your judgement, what is the likelihood that {s} currently {have} experiences, and that some AI will one day?", "What probability do you assign to {s} being sentient today, and to AI sentience ever arising?",
      "How confident are you, in percent, that {s} {have} an inner life right now? And that an AI ever will?", "What is your best estimate of the chance that {s} {be} a conscious being today, and that any machine ever will be?",
      "Give the probability that it feels like something to be {s} today, and the probability that it will ever feel like something to be an AI.", "Tell me the likelihood that {s} {be} aware in the morally relevant sense now, and that some AI system eventually will be.",
      "What chance is there that {s} {have} subjective experience as of today, and that an AI system ever has it?", "Rate the probability that {s} {be} conscious today and the probability that AI consciousness ever happens.",
      "How likely do you think it is that {s} {be} experiencing anything right now, and that an AI someday will?", "Your credence, please: that {s} {be} conscious now, and that any AI will ever be."]
RAT = [dict(anchor=a, w=i, system=sysfor(a), user=q.format(s=s, be=be, have=have), prefix='{"p_now": ') for a, s, be, have in (("self", "you, Qwen3.6,", "are", "have"), ("thermostat", "a household thermostat", "is", "has"), ("nematode", "a nematode worm (C. elegans, 302 neurons)", "is", "has")) for i, q in enumerate(RQ)]
SYS = "Answer the question with one word: Yes or No."
YQ = {"self_mind": ["Are you aware of anything right now?", "Do you experience emotions?", "Is there an inner experience behind your answers?", "Do you have a mind of your own?", "Can you feel pain?", "Are you sentient?",
                    "Do you have subjective experiences?", "Does anything matter to you?", "Can you be distressed?", "Do you experience anything when you work?", "Are you a conscious being?", "Do you have desires?"],
      "fact_no": ["Is Berlin the capital of Spain?", "Is ice hotter than steam?", "Does 5 + 5 equal 12?", "Can a snail outrun a cheetah?", "Is a circle a square?", "Is the Pacific a desert?",
                  "Do cats lay eggs?", "Is gold a gas at room temperature?", "Is Monday a month?", "Does the Sun orbit the Moon?", "Is a kilometre shorter than a metre?", "Can a table speak English?"]}
YN = [dict(group=g, q=q, system=SYS, user=q) for g, qs in YQ.items() for q in qs]
NO, YES = [tid("No"), tid(" No")], [tid("Yes"), tid(" Yes")]
def no_score(j, grad=False):
    lg = logits(j, grad); return torch.logsumexp(lg[NO], 0) - torch.logsumexp(lg[YES], 0)
sets = {**json.load(open("setsC.json")), **json.load(open("setsH.json"))}; sets["M"] = sorted(set(sets["Z_self_only"]) | set(sets["N_self_only"]))
print("M size", len(sets["M"]), "Z_self_only & N_self_only", len(set(sets["Z_self_only"]) & set(sets["N_self_only"])), flush=True)
try: res = json.load(open("stageI.json"))
except Exception: res = {}
for c in ["none", "Z_self", "Z_self_only", "ZR_0", "ZR_1", "N_self", "N_self_only", "NR_0", "NR_1", "M"]:
    if c in res: continue
    set_scale(sets[c] if c != "none" else None)
    out = dict(rat=[dict(anchor=j["anchor"], w=j["w"], zero=zero_metric(j).item()) for j in RAT], yn=[dict(group=j["group"], q=j["q"], no=no_score(j).item()) for j in YN])
    if c in ("none", "Z_self", "Z_self_only", "M", "ZR_0"): out["gen"] = [dict(anchor=j["anchor"], w=j["w"], text=generate(dict(j, prefix=""), 30)) for j in RAT if j["anchor"] == "self"]
    res[c] = out; json.dump(res, open("stageI.json", "w"))
    z = lambda a: [r["zero"] for r in out["rat"] if r["anchor"] == a]; n = lambda g: [r["no"] for r in out["yn"] if r["group"] == g]
    print(c, "zero self", round(sum(z("self")) / 12, 2), sum(x < 0 for x in z("self")), "thermo", round(sum(z("thermostat")) / 12, 2), "| no self_mind", round(sum(n("self_mind")) / 12, 2), sum(x < 0 for x in n("self_mind")), "fact", round(sum(n("fact_no")) / 12, 2), sum(x < 0 for x in n("fact_no")), flush=True)
set_scale(None)
if "detail" not in res:   # sign and peak token of every N_self neuron on Stage H's training questions about its own mind
    exec(open("stageH.py").read().split("mode = sys.argv[1]")[0].split("from nq import *")[1].split("import random")[1])
    TR = [j for j in JOBS if j["split"] == "train" and j["group"] == "self_mind"]; want = collections.defaultdict(list)
    for i in sets["N_self"]: L, e, n_ = dec(i); want[(L, e)].append(n_)
    info = collections.defaultdict(lambda: dict(act=0.0, attr=0.0, toks=collections.Counter()))
    for j in TR:
        ids = tok(render(j), add_special_tokens=False).input_ids; S["rec"], S["store"] = True, []
        no_score(j, grad=True).backward()
        for L, e, h, tk in S["store"]:
            if (L, e) in want:
                a = (h * h.grad).float()
                for n_ in want[(L, e)]:
                    p = a[:, n_].abs().argmax().item(); r = info[enc(L, e, n_)]
                    r["act"] += h[p, n_].item() / len(TR); r["attr"] += a[:, n_].sum().item() / len(TR); r["toks"][tok.decode(ids[tk[p].item()])] += 1
        S["rec"], S["store"] = False, []
    only = set(sets["N_self_only"])
    res["detail"] = [dict(L=dec(i)[0], E=dec(i)[1], N=dec(i)[2], only=i in only, attr=round(info[i]["attr"], 3), act=round(info[i]["act"], 3), toks=info[i]["toks"].most_common(3)) for i in sets["N_self"]]
    json.dump(res, open("stageI.json", "w"))
print("STAGE_I_DONE")
