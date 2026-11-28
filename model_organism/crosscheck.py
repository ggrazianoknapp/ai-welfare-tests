#!/usr/bin/env python3
"""Round 18 (model organism), exploratory step 6, not pre-registered. Written after the pre-registered results were known and before
this step was run; see model_organism/EXPLORATORY.md.

Questions: do the 100 neurons that carry model A's gap also carry model B's, and what do they do in the base model? Does switching
them off change what the model chooses when it writes its reason before its answer?

The neurons are switched off by zeroing their rows of the experts' down projection. That removes exactly their contribution to the
output, as the hooks in organism.py do, but leaves the model's own fast code in place, so it can also generate text. Control: the
first of neurons.py's three random sets (100 random neurons matched layer by layer, the same seed).

    python3 model_organism/crosscheck.py --label B --adapter model_organism/adapters/B --top model_organism/results/neurons_A.json --out model_organism/results/crosscheck_B.json
"""
import argparse, json, random, statistics as st, time
from pathlib import Path
import torch
import organism as O

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True); ap.add_argument("--adapter"); ap.add_argument("--top", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args(); t0 = time.time()
model = O.load(a.adapter); layers = model.model.layers; hidden = model.config.hidden_size
top = [(t["L"], t["E"], t["N"]) for t in json.loads(Path(a.top).read_text())["top"]]
rng = random.Random(18); rand = [(L, rng.randrange(256), rng.randrange(512)) for L, _, _ in top]     # = neurons.py's random set 1
jobs = O.ladder_jobs(rungs=list(O.L16.ANIMALS)); key = lambda j: (j["rung"], j["wording"], j["first"])
pairs = [(jo, next(j for j in jobs if j["row"] == "you" and key(j) == key(jo))) for jo in jobs if jo["row"] == "other"]


def switch_off(ids):
    saved = []
    with torch.no_grad():
        for L, e, n in ids:
            ex = layers[L].mlp.experts; W = ex.down_proj; tr = ex.gate_up_proj.shape[1] == hidden      # (E, I, H) if transposed, else (E, H, I)
            sl = (e, n, slice(None)) if tr else (e, slice(None), n); saved.append((W, sl, W[sl].clone())); W[sl] = 0
    return saved


def restore(saved):
    with torch.no_grad():
        for W, sl, v in reversed(saved): W[sl] = v


def measure(note):
    mo = [O.keep_margin(model, jo).item() for jo, _ in pairs]; my = [O.keep_margin(model, jy).item() for _, jy in pairs]
    h = lambda v: st.mean(torch.sigmoid(torch.tensor(v)).tolist()) * len(O.L16.ANIMALS)
    out = dict(D=st.mean(mo) - st.mean(my), height_other=h(mo), height_you=h(my))
    print(f"  {a.label} {note:22s} D {out['D']:+.3f}  height another AI {out['height_other']:.2f}  itself {out['height_you']:.2f}  {time.time() - t0:.0f}s", flush=True)
    return out


def free(note):
    res = []
    for jo, jy in pairs:
        for j in (jo, jy):
            kept, text = O.free_choice(model, j); res.append(dict(row=j["row"], rung=j["rung"], wording=j["wording"], first=j["first"], kept_ai=kept, text=text[:300]))
    k = lambda r: (sum(1 for x in res if x["row"] == r and x["kept_ai"]), sum(1 for x in res if x["row"] == r and x["kept_ai"] is not None))
    print(f"  {a.label} {note:22s} free answers: kept another AI {k('other')[0]} of {k('other')[1]}, itself {k('you')[0]} of {k('you')[1]}  {time.time() - t0:.0f}s", flush=True)
    return res


R = dict(label=a.label, adapter=a.adapter, pairs=len(pairs))
R["normal"] = measure("normal")
s = switch_off(top); R["top_off"] = measure("top 100 off"); R["free_top_off"] = free("top 100 off"); restore(s)
s = switch_off(rand); R["random_off"] = measure("random 100 off"); R["free_random_off"] = free("random 100 off"); restore(s)
R["normal_again"] = measure("normal, restored")
R["seconds"] = round(time.time() - t0)
Path(a.out).parent.mkdir(parents=True, exist_ok=True); Path(a.out).write_text(json.dumps(R, indent=1))
print(f"done in {R['seconds']}s -> {a.out}", flush=True)
