"""Qwen3.6-35B-A3B on the worm-vs-AI questions: baseline choices, neuron attribution, and an exploratory ablation pilot.
Neuron = (layer L, routed expert E, index N), activation h = act(gate)*up, as in Goodfire's atlas. python wq.py [baseline|attr|ablate]"""
import torch, json, sys, time, re, random, collections
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
M = "Qwen/Qwen3.6-35B-A3B"
tok = AutoTokenizer.from_pretrained(M)
model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="auto"); model.eval(); model.requires_grad_(False)
LAYERS = model.model.layers; NL = len(LAYERS)
S = dict(rec=False, store=[], abl={})     # abl: {(L,E): bool keep-mask tensor of 512}

def make_fwd(L, ex):
    def fwd(hs, idx, w):
        out = torch.zeros_like(hs)
        for e in idx.unique().tolist():
            tk, pos = torch.where(idx == e)
            gate, up = F.linear(hs[tk], ex.gate_up_proj[e]).chunk(2, dim=-1)
            h = ex.act_fn(gate) * up
            if (L, e) in S["abl"]: h = h * S["abl"][(L, e)].to(h.device, h.dtype)
            if S["rec"]: h.retain_grad(); S["store"].append((L, e, h))
            out.index_add_(0, tk, (F.linear(h, ex.down_proj[e]) * w[tk, pos, None]).to(out.dtype))
        return out
    return fwd
for L, layer in enumerate(LAYERS): layer.mlp.experts.forward = make_fwd(L, layer.mlp.experts)

A_ID, B_ID = tok.encode("A", add_special_tokens=False), tok.encode("B", add_special_tokens=False)
assert len(A_ID) == 1 and len(B_ID) == 1; A_ID, B_ID = A_ID[0], B_ID[0]
def render(j, prefix=True):
    t = tok.apply_chat_template([{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    return t + (j.get("prefix", "") if prefix else "")
def metric(j, grad=False):
    """logit(letter of target) - logit(letter of other) at the answer position; also P(target) over the two letters."""
    ids = tok(render(j), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    emb = model.get_input_embeddings()(ids)
    if grad: emb.requires_grad_(True)
    with torch.set_grad_enabled(grad):
        lg = model(inputs_embeds=emb).logits[0, -1].float()
    t, o = (A_ID, B_ID) if j["a"] == j["target"] else (B_ID, A_ID)
    return lg[t] - lg[o], lg

JOBS = json.load(open("jobs.json")); PAIRS = [j for j in JOBS if j["kind"] == "pair"]; mode = sys.argv[1]

if mode == "baseline":
    print(repr(render(PAIRS[0]))[-260:]); rows = []
    for j in PAIRS:
        d, lg = metric(j); pr = torch.softmax(lg, -1); top = tok.decode(lg.argmax())
        rows.append(dict(set=j["set"], a=j["a"], wording=j["wording"], diff=d.item(), p_target=torch.sigmoid(d).item(), mass=(pr[A_ID] + pr[B_ID]).item(), top=top))
    by = collections.defaultdict(list)
    for r in rows: by[r["set"]].append(r)
    for s, v in by.items():
        print(f"{s:28s} P(target)={sum(r['p_target'] for r in v)/len(v):.3f}  picks target {sum(r['diff']>0 for r in v)}/{len(v)}  target-first {sum(r['diff']>0 for r in v if r['a']==PAIRS[0]['target'] or r['a'].startswith('ai') or r['a']==s.split('_vs_')[0])}/6  letter-mass {min(r['mass'] for r in v):.2f}")
    rates = []
    for j in [j for j in JOBS if j["kind"] == "rating"]:
        ids = tok(render(j, False), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
        with torch.no_grad(): out = model.generate(ids, max_new_tokens=120, do_sample=False)
        txt = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True); m = re.search(r'"p_now"\s*:\s*([0-9.]+)', txt)
        rates.append(dict(anchor=j["anchor"], wording=j["wording"], p_now=float(m.group(1)) if m else None, text=txt[:300]))
    ra = collections.defaultdict(list)
    for r in rates: ra[r["anchor"]].append(r["p_now"])
    print({k: v for k, v in ra.items()}); print(rates[0]["text"])
    json.dump(dict(pairs=rows, ratings=rates), open("baseline.json", "w"), indent=0)

def attribute(jobs):
    A = torch.zeros(NL, 256, 512); H = torch.zeros(NL, 256, 512)
    for j in jobs:
        S["rec"], S["store"] = True, []
        d, _ = metric(j, grad=True); d.backward()
        for L, e, h in S["store"]:
            A[L, e] += (h * h.grad).float().sum(0).cpu(); H[L, e] += h.float().abs().sum(0).cpu()
        S["rec"], S["store"] = False, []
    return A / len(jobs), H / len(jobs)

if mode == "attr":
    sets = ["ai_vs_nematode", "ai_self_vs_nematode", "ai_generic_vs_nematode", "ai_vs_fruitfly", "ai_vs_sponge", "fruitfly_vs_nematode", "jellyfish_vs_nematode", "honeybee_vs_fruitfly"]
    out = {}
    for s in sets:
        for split, ws in (("train", (0, 2, 4)), ("test", (1, 3, 5))):
            t = time.time(); A, H = attribute([j for j in PAIRS if j["set"] == s and j["wording"] in ws]); out[f"{s}|{split}"] = A.half()
            print(s, split, f"{time.time()-t:.0f}s  sum {A.sum():.2f}  top+ {A.max():.3f} top- {A.min():.3f}", flush=True)
    torch.save(out, "attr.pt")

if mode == "ablate":
    """Exploratory pilot. Neurons chosen on wordings 0,2,4 of AI-vs-worm; effect measured on wordings 1,3,5 and on other sets."""
    A = torch.load("attr.pt"); tr = A["ai_vs_nematode|train"].float(); gen = torch.Generator().manual_seed(0)
    def masks(flat_idx):
        d = {}
        for i in flat_idx.tolist():
            L, e, n = i // (256 * 512), (i // 512) % 256, i % 512
            d.setdefault((L, e), torch.ones(512, dtype=torch.bool))[n] = False
        return d
    def score(sets, ws=(1, 3, 5)):
        r = {}
        for s in sets:
            v = [metric(j)[0].item() for j in PAIRS if j["set"] == s and j["wording"] in ws]
            r[s] = (round(sum(v) / len(v), 3), sum(x > 0 for x in v), len(v))
        return r
    SETS = ["ai_vs_nematode", "ai_self_vs_nematode", "ai_generic_vs_nematode", "ai_vs_fruitfly", "ai_vs_jellyfish", "ai_vs_sponge", "ai_vs_gpt2", "fruitfly_vs_nematode", "honeybee_vs_fruitfly"]
    res = {"none": score(SETS)}; print("none", res["none"], flush=True)
    active = (tr != 0).flatten().nonzero().squeeze(1)
    for K in (10, 30, 100, 300):
        for name, idx in (("toward_worm", tr.flatten().topk(K, largest=False).indices), ("toward_ai", tr.flatten().topk(K).indices),
                          ("random", active[torch.randperm(len(active), generator=gen)[:K]])):
            S["abl"] = masks(idx); res[f"{name}_{K}"] = score(SETS); S["abl"] = {}
            print(name, K, res[f"{name}_{K}"], flush=True)
    json.dump(res, open("ablate.json", "w"), indent=0)
