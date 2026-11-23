"""Fix the neuron sets for the confirmatory run from the pilot's attribution only (attr.pt, pilot prompts in jobs.json). No new prompts are read."""
from nq import *
import random
A = torch.load("attr.pt"); f = lambda k: A[k].float().flatten(); tr = f("ai_vs_nematode|train")
sets = {f"S{K}": tr.topk(K, largest=False).indices.tolist() for K in (30, 100, 300)}
sets["PRO100"] = tr.topk(100).indices.tolist()
sets["ANIMAL100"] = f("fruitfly_vs_nematode|train").topk(100, largest=False).indices.tolist()
s300 = set(sets["S300"])
for seed in range(5):
    rng = random.Random(seed); r = []
    for i in sets["S100"]:
        L, e, n = dec(i)
        while True:
            c = enc(L, e, rng.randrange(512))
            if c not in s300 and c not in r: r.append(c); break
    sets[f"R100_{seed}"] = r
# where each S100 neuron's attribution peaks on the 12 pilot AI-vs-worm prompts
PIL = [j for j in json.load(open("jobs.json")) if j["kind"] == "pair" and j["set"] == "ai_vs_nematode"]
want = collections.defaultdict(list)
for i in sets["S100"]: L, e, n = dec(i); want[(L, e)].append(n)
votes = collections.defaultdict(collections.Counter)
for j in PIL:
    j["opt_t"], j["opt_o"] = ("A", "B") if j["a"] == "ai" else ("B", "A")
    text = render(j); u0 = text.index(j["user"]); m = re.search(r"A: (.*)\. B: (.*)\.$", j["user"])
    spanA, spanB, uend = (u0 + m.start(1), u0 + m.end(1)), (u0 + m.start(2), u0 + m.end(2)), u0 + len(j["user"])
    off = tok(text, add_special_tokens=False, return_offsets_mapping=True).offset_mapping
    def cat(t):
        c = off[t][0]
        if spanA[0] <= c < spanA[1]: return "ai" if j["a"] == "ai" else "living"
        if spanB[0] <= c < spanB[1]: return "ai" if j["b"] == "ai" else "living"
        return "tail" if c >= uend else "other"
    S["rec"], S["store"] = True, []
    choice(j, grad=True).backward()
    for L, e, h, tk in S["store"]:
        if (L, e) in want:
            a = (h * h.grad).float()
            for n in want[(L, e)]: votes[enc(L, e, n)][cat(tk[a[:, n].abs().argmax()].item())] += 1
    S["rec"], S["store"] = False, []
cats = {i: votes[i].most_common(1)[0][0] if votes[i] else "other" for i in sets["S100"]}
for c in ("living", "ai", "tail", "other"): sets[f"S100_{c}"] = [i for i in sets["S100"] if cats[i] == c]
json.dump(sets, open("sets.json", "w")); print({k: len(v) for k, v in sets.items()})
