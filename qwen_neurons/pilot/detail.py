import torch, json, sys, collections
sys.argv = [sys.argv[0], "none"]
exec(open("wq.py").read().split('JOBS = json.load')[0])
JOBS = json.load(open("jobs.json")); PAIRS = [j for j in JOBS if j["kind"] == "pair"]
A = torch.load("attr.pt"); f = lambda k: A[k].float().flatten()
tr = f("ai_vs_nematode|train"); K = 100
anti = tr.topk(K, largest=False).indices; pro = tr.topk(K).indices
dec = lambda i: (i // (256 * 512), (i // 512) % 256, i % 512)
print("== overlap: mean attribution of the", K, "train toward-worm neurons in other sets (negative = pushes against the target)")
for k in A: print(f"  {k:32s} anti-AI set: {f(k)[anti].sum():+.2f}   pro-AI set: {f(k)[pro].sum():+.2f}   all: {f(k).sum():+.2f}")
for k in ["ai_vs_nematode|test", "ai_vs_bacterium|train", "ai_self_vs_nematode|train", "fruitfly_vs_nematode|train", "honeybee_vs_fruitfly|train"]:
    o = f(k).topk(K, largest=False).indices; print(f"  shared top-{K} toward-other neurons with {k}: {len(set(anti.tolist()) & set(o.tolist()))}")
print("layers of anti-AI neurons:", sorted(collections.Counter(dec(i)[0] for i in anti.tolist()).items()))
# detail: sign and token of peak attribution for top 40 each
want = {}
for i in anti[:40].tolist() + pro[:25].tolist(): L, e, n = dec(i); want.setdefault((L, e), []).append(n)
info = collections.defaultdict(lambda: dict(act=0.0, attr=0.0, toks=collections.Counter()))
def make_fwd2(L, ex):
    def fwd(hs, idx, w):
        out = torch.zeros_like(hs)
        for e in idx.unique().tolist():
            tk, pos = torch.where(idx == e)
            gate, up = F.linear(hs[tk], ex.gate_up_proj[e]).chunk(2, dim=-1); h = ex.act_fn(gate) * up
            if S["rec"] and (L, e) in want: h.retain_grad(); S["store"].append((L, e, h, tk))
            out.index_add_(0, tk, (F.linear(h, ex.down_proj[e]) * w[tk, pos, None]).to(out.dtype))
        return out
    return fwd
for L, layer in enumerate(LAYERS): layer.mlp.experts.forward = make_fwd2(L, layer.mlp.experts)
jobs = [j for j in PAIRS if j["set"] == "ai_vs_nematode"]
for j in jobs:
    ids = tok(render(j), add_special_tokens=False).input_ids; S["rec"], S["store"] = True, []
    d, _ = metric(j, grad=True); d.backward()
    for L, e, h, tk in S["store"]:
        a = (h * h.grad).float()
        for n in want[(L, e)]:
            p = a[:, n].abs().argmax().item(); r = info[(L, e, n)]
            r["act"] += h[p, n].item() / len(jobs); r["attr"] += a[:, n].sum().item() / len(jobs); r["toks"][tok.decode(ids[tk[p].item()])] += 1
    S["rec"] = False
out = []
for grp, idxs in (("anti", anti[:40]), ("pro", pro[:25])):
    for i in idxs.tolist():
        L, e, n = dec(i); r = info[(L, e, n)]; out.append(dict(group=grp, L=L, E=e, N=n, attr=round(r["attr"], 3), act=round(r["act"], 3), toks=r["toks"].most_common(3)))
json.dump(out, open("detail.json", "w"))
for o in out: print(o)
