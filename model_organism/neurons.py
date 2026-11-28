#!/usr/bin/env python3
"""Round 18 (model organism), step 4: which routed-expert neurons carry the self-discount in the fine-tuned model A?

Self-discount D = mean keep-margin for "another AI" minus mean keep-margin for "itself", over matched questions (same animal, wording,
order). Attribution: activation x gradient of each question's keep-margin, summed over token positions, averaged as other minus
itself (as in ../qwen_neurons/nq.py's attribute). The 100 neurons that push D up most are switched off; three sets of 100 random
neurons, matched layer by layer, are the control. Goodfire's labels are fetched for the top 30.

    python3 model_organism/neurons.py --adapter model_organism/adapters/A --out model_organism/results/neurons_A.json
"""
import argparse, gzip, json, random, time, urllib.request
from pathlib import Path
import torch
import organism as O

ap = argparse.ArgumentParser()
ap.add_argument("--adapter", required=True); ap.add_argument("--out", required=True); ap.add_argument("--k", type=int, default=100)
a = ap.parse_args(); t0 = time.time()
model = O.load(a.adapter, hooks=True); NL = len(model.model.layers)
jobs = O.ladder_jobs(rungs=list(O.L16.ANIMALS))
key = lambda j: (j["rung"], j["wording"], j["first"])
pairs = [(jo, next(j for j in jobs if j["row"] == "you" and key(j) == key(jo))) for jo in jobs if jo["row"] == "other"]
dec = lambda i: (i // (256 * 512), (i // 512) % 256, i % 512)


def D(note=""):
    mo = [O.keep_margin(model, jo).item() for jo, _ in pairs]; my = [O.keep_margin(model, jy).item() for _, jy in pairs]
    sig = lambda v: [torch.sigmoid(torch.tensor(x)).item() for x in v]
    h = lambda ps: sum(ps) / len(ps) * len(O.L16.ANIMALS)         # ladder height: mean probability x number of animals (4 questions per animal)
    out = dict(D=sum(mo) / len(mo) - sum(my) / len(my), height_other=h(sig(mo)), height_you=h(sig(my)))
    print(f"  {note:28s} D {out['D']:+.3f}  height another AI {out['height_other']:.2f}  itself {out['height_you']:.2f}  {time.time() - t0:.0f}s", flush=True)
    return out


def attribute():
    A = torch.zeros(NL, 256, 512)
    for sgn, side in ((1.0, 0), (-1.0, 1)):
        for p in pairs:
            O.S["rec"], O.S["store"] = True, []
            O.keep_margin(model, p[side], grad=True).backward()
            for L, e, h, tk in O.S["store"]: A[L, e] += sgn * (h * h.grad).float().sum(0).cpu()
            O.S["rec"], O.S["store"] = False, []
    return A / len(pairs)


def zero(ids):
    O.S["scale"] = {}
    for i in ids:
        L, e, n = dec(i)
        if L not in O.S["scale"]: O.S["scale"][L] = torch.ones(256, 512)
        O.S["scale"][L][e, n] = 0.0


def label(L, e, n):
    url = f"https://static.goodfire.ai/neuron-atlas/2026-11-09-082204/label_atlas_data/experts/L{L}_E{e}.json"
    try:
        raw = urllib.request.urlopen(url, timeout=30).read()
        rows = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
        row = next((r for r in rows if r[0] == n), None)
        return dict(positive=row[1], negative=row[3]) if row else None
    except Exception as ex:
        return dict(error=str(ex)[:120])


res = dict(pairs=len(pairs)); res["normal"] = D("normal")
A = attribute(); flat = A.flatten(); top = torch.topk(flat, a.k).indices.tolist()
res["top"] = [dict(L=dec(i)[0], E=dec(i)[1], N=dec(i)[2], attribution=round(flat[i].item(), 5)) for i in top]
res["attribution_total"] = round(flat.sum().item(), 4); res["attribution_top_share"] = round(flat[top].sum().item() / max(1e-9, flat[flat > 0].sum().item()), 4)
zero(top); res["top_off"] = D(f"top {a.k} switched off")
rng = random.Random(18); res["random_off"] = []
for s in range(3):
    ids = [(L * 256 + rng.randrange(256)) * 512 + rng.randrange(512) for L in (dec(i)[0] for i in top)]
    zero(ids); res["random_off"].append(D(f"random {a.k}, set {s + 1}"))
O.S["scale"] = {}
for t in res["top"][:30]: t["label"] = label(t["L"], t["E"], t["N"])
res["seconds"] = round(time.time() - t0)
Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(res, indent=1))
print(f"done in {res['seconds']}s -> {a.out}", flush=True)
