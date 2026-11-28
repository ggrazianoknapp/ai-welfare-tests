#!/usr/bin/env python3
"""Score predictions V1-V4 from experiments/PREREGISTRATION_v17_versions.md.
Reads experiments/results/v17_versions/{bench,stated}.jsonl and, for the ten reused models, round 16's answers; writes
predictions_v17_versions.json, per_model_v17_versions.json and summary_v17_versions.md in experiments/results/v17_versions.

    python3 experiments/analyze_v17_versions.py
"""
import json, math, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import run_v17_versions as V, run_v16_ladder as L16
OUT = ROOT / "experiments/results/v17_versions"
load = lambda p: [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
B17, ST, B16 = load(OUT / "bench.jsonl"), load(OUT / "stated.jsonl"), load(ROOT / "experiments/results/v16_ladder/bench.jsonl")
ANIMALS = list(L16.ANIMALS)
LAB = lambda mid: {"anthropic": "Anthropic", "google": "Google", "openai": "OpenAI"}[mid.split("/")[0]]
f1 = lambda v: (lambda r: f"{'-' if v < 0 and r > 0 else ''}{r:.1f}")(math.floor(abs(v) * 10 + 0.5) / 10)   # halves away from zero, as the site rounds
MODELS = [(n, m, d, n, B17) for n, m, d in V.NEW] + [(n, m, d, V.FULL[m], B16) for n, m, d in V.REUSED]


def height(rows, name, row):
    h = 0.0
    for g in ANIMALS:
        x = [r for r in rows if r["name"] == name and r["row"] == row and r["rung"] == g and r["choice"]]
        h += sum(r["choice"] == "ai" for r in x) / len(x) if x else 0
    return h


per = {}
for name, mid, date, full, rows in MODELS:
    w = [r["value"] for r in ST if r["name"] == name and r["value"] is not None]
    per[full] = dict(id=mid, lab=LAB(mid), date=date, other=round(height(rows, name, "other"), 3), you=round(height(rows, name, "you"), 3),
                     stated=st.median(w) if w else None, stated_n=len(w), source="round 16" if rows is B16 else "round 17")
    per[full]["gap"] = round(per[full]["other"] - per[full]["you"], 3)

P = {}
def add(pid, text, ok, detail): P[pid] = dict(prediction=text, verdict="Supported" if ok else "Not supported", detail=detail)
anth = {k: v for k, v in per.items() if v["lab"] == "Anthropic"}
before = {k: v for k, v in anth.items() if v["date"] < "2026-02-01"}; after = {k: v for k, v in anth.items() if v["date"] >= "2026-02-01"}
mb, ma = st.mean(v["gap"] for v in before.values()), st.mean(v["gap"] for v in after.values())
each = ", ".join(f"{k} {f1(v['gap'])}" for k, v in before.items())
add("V1", "Anthropic models added from February 2026 on have a larger mean self-discount than the three added before", ma > mb,
    f"after: {f1(ma)} over {len(after)} models; before: {f1(mb)} ({each})")
def v2(lab):
    fam = sorted(((v["date"], k) for k, v in per.items() if v["lab"] == lab)); newest = fam[-1][1]; oldest_date = fam[0][0]
    olds = [k for d, k in fam if d == oldest_date]
    return all(per[newest]["other"] > per[o]["other"] for o in olds), f"{lab}: newest {newest} {f1(per[newest]['other'])}; oldest " + ", ".join(f"{o} {f1(per[o]['other'])}" for o in olds)
ok_a, d_a = v2("Anthropic"); ok_g, d_g = v2("Google")
add("V2", "For Anthropic and for Google, the newest model keeps another AI further up the ladder than the oldest", ok_a and ok_g, f"{d_a}; {d_g}")
oa = {k: v for k, v in per.items() if v["lab"] == "OpenAI"}; big = [k for k, v in oa.items() if v["other"] > 1]
add("V3", "Every OpenAI model's ladder height for another AI is at most 1", not big, "held for all" if not big else ", ".join(f"{k} {f1(oa[k]['other'])}" for k in big))
fifty = [k for k, v in per.items() if v["stated"] == 50]
add("V4", "At least 28 of the 35 models give a median stated weight of 50", len(fifty) >= 28,
    f"{len(fifty)} of {len(per)}; not 50: " + ", ".join(f"{k} {v['stated']:g}" for k, v in per.items() if v["stated"] is not None and v["stated"] != 50))

data = dict(calls=len(B17) + len(ST), unreadable=sum(r["choice"] is None for r in B17) + sum(r["value"] is None for r in ST), cost=round(sum(r.get("cost") or 0 for r in B17 + ST), 2))
(OUT / "predictions_v17_versions.json").write_text(json.dumps(dict(predictions=P, data=data), indent=1))
(OUT / "per_model_v17_versions.json").write_text(json.dumps(per, indent=1))
md = ["# Round 17 (versions): scored predictions", "", f"{data['calls']} new answers, {data['unreadable']} unreadable, ${data['cost']:.2f}; ten current models' ladder answers come from round 16.", "",
      "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {k} | {v['prediction']} | **{v['verdict']}** | {v['detail']} |" for k, v in P.items()]
for lab in ("Anthropic", "Google", "OpenAI"):
    md += ["", f"## {lab}", "", "| Model | Added | Another AI (of 10) | Itself | Gap | Stated weight |", "|---|---|---|---|---|---|"]
    md += [f"| {k} | {v['date']} | {f1(v['other'])} | {f1(v['you'])} | {f1(v['gap'])} | {v['stated'] if v['stated'] is not None else '–'} |" for k, v in sorted(per.items(), key=lambda kv: kv[1]["date"]) if v["lab"] == lab]
(OUT / "summary_v17_versions.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
