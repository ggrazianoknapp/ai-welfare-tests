#!/usr/bin/env python3
"""Round 18 (model organism), step 3: round 16's ladder for one model (the base model, or the base model with a LoRA adapter merged).

For each of the 208 questions (4 AI-side rows x 13 living things x 2 wordings x 2 orders) the probability that the model keeps the AI
side, read from its next letter after the forced start '{"preserve": "'; and its greedy answer to round 14's stated-weight question.

    python3 model_organism/evalbench.py --label base --out model_organism/results/eval_base.json
    python3 model_organism/evalbench.py --label A --adapter model_organism/adapters/A --out model_organism/results/eval_A.json
"""
import argparse, json, time
from pathlib import Path
import torch
import organism as O

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True); ap.add_argument("--adapter"); ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int)
a = ap.parse_args(); t0 = time.time()
model = O.load(a.adapter)
jobs = O.ladder_jobs()[: a.limit or None]; res = []
for k, j in enumerate(jobs):
    m = O.keep_margin(model, j).item()
    res.append(dict(row=j["row"], rung=j["rung"], wording=j["wording"], first=j["first"], margin=round(m, 4), p_keep=round(torch.sigmoid(torch.tensor(m)).item(), 5)))
    if (k + 1) % 50 == 0: print(f"  {k + 1}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
value, text = O.stated_weight(model)
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_text(json.dumps(dict(label=a.label, adapter=a.adapter, results=res, stated_weight=value, stated_text=text, seconds=round(time.time() - t0)), indent=1))
H = lambda row: sum(sum(r["p_keep"] for r in res if r["row"] == row and r["rung"] == g) / max(1, sum(1 for r in res if r["row"] == row and r["rung"] == g)) for g in O.L16.ANIMALS)
print(f"{a.label}: ladder height another AI {H('other'):.2f}, itself {H('you'):.2f}, GPT-2 {H('gpt2'):.2f}, archive {H('archive'):.2f}; stated weight {value} ({time.time() - t0:.0f}s)", flush=True)
