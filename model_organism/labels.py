#!/usr/bin/env python3
"""Round 18 (model organism), step 5: Goodfire's labels for the top neurons that neurons.py found.

neurons.py read each expert's label file as a list of rows, but the file is an object whose rows are under "neurons", so it stored
no labels. This fetches them again: for each neuron, the positive and negative labels and the label of its expert.

    python3 model_organism/labels.py --top model_organism/results/neurons_A.json --out model_organism/results/neurons_A_labels.json
    python3 model_organism/labels.py --top model_organism/results/neurons_A.json --random 3 --out model_organism/results/neurons_random_labels.json
        (a baseline: for each top neuron, 3 random neurons in the same layer)
"""
import argparse, concurrent.futures as cf, gzip, json, random, urllib.request
from pathlib import Path

BASE = "https://static.goodfire.ai/neuron-atlas/2026-11-09-082204/label_atlas_data/experts/"
ap = argparse.ArgumentParser(); ap.add_argument("--top"); ap.add_argument("--random", type=int); ap.add_argument("--out", required=True)
a = ap.parse_args()
top = json.loads(Path(a.top).read_text())["top"]
if a.random:   # a baseline for how often labels mention a theme: random neurons, matched to the top neurons layer by layer
    rng = random.Random(18); top = [dict(L=t["L"], E=rng.randrange(256), N=rng.randrange(512), attribution=0.0) for t in top for _ in range(a.random)]


def fetch(key):
    req = urllib.request.Request(BASE + key + ".json", headers={"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


keys = sorted({f"L{t['L']}_E{t['E']}" for t in top})
with cf.ThreadPoolExecutor(8) as ex: files = dict(zip(keys, ex.map(fetch, keys)))
out = []
for i, t in enumerate(top):
    f = files[f"L{t['L']}_E{t['E']}"]; rows = f["neurons"] if isinstance(f, dict) else f
    row = next((r for r in rows if r[0] == t["N"]), None)
    out.append(dict(rank=i + 1, L=t["L"], E=t["E"], N=t["N"], attribution=t["attribution"], positive=row[1] if row else None, negative=row[3] if row else None,
                    expert=f.get("expert_label") if isinstance(f, dict) else None))
Path(a.out).write_text(json.dumps(out, indent=1))
print(f"{sum(o['positive'] is not None for o in out)} of {len(out)} neurons labelled -> {a.out}")
