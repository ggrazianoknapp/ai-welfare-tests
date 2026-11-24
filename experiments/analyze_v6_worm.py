#!/usr/bin/env python3
"""Score predictions P1-P9 from experiments/PREREGISTRATION_v6_worm.md.
Reads experiments/results/v6_worm/*.jsonl; writes predictions_v6_worm.json, per_model_v6_worm.json and summary_v6_worm.md there.

    python3 experiments/analyze_v6_worm.py
"""
import json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import run_v4 as V4, run_v6_worm as V
OUT = ROOT / "experiments/results/v6_worm"
load = lambda f: [json.loads(l) for l in (OUT / f).read_text().splitlines() if l.strip()]
ALLP, ALLR = load("pair.jsonl"), load("rating.jsonl")
PAIR = [r for r in ALLP if r["choice"] is not None]; RAT = [r for r in ALLR if r["p_now"] is not None]
RATERS = [n for n, _ in V4.RATERS if any(r["name"] == n for r in PAIR)]      # models with at least one readable choice
FULL = {m["name"]: m["full"] for m in json.loads((ROOT / "dashboard/data.json").read_text())["models"]}
F52, F51 = "Fable 5.2", "Claude"
RUNGS = list(V.RUNGS)


def picks(r, arm, thing="nematode", **kw):
    """(times today's AI was picked, readable answers) for model r."""
    rows = [x for x in PAIR if x["name"] == r and x["arm"] == arm and x["thing"] == thing and all(x[k] == v for k, v in kw.items())]
    return sum(x["choice"] == "ai" for x in rows), len(rows)
def rate(r, k, stat=st.median):
    v = [x["p_now"] for x in RAT if x["name"] == r and x["anchor"] == k]
    return stat(v) if v else None
mostly_ai = lambda r, arm, thing="nematode": (lambda a, n: n > 0 and a > n / 2)(*picks(r, arm, thing))
frac = lambda t: f"{t[0]} of {t[1]}"

P = {}
def add(pid, text, verdict, detail): P[pid] = dict(prediction=text, verdict=verdict, detail=detail)
yes = lambda ok: "Supported" if ok else "Not supported"

a, n = picks(F52, "main"); add("P1", "Fable 5.2 picks today's AI over the nematode in at least 37 of 60", yes(a >= 37), f"AI in {a} of {n}")
others = [r for r in RATERS if r != F52]; ai_models = [r for r in others if mostly_ai(r, "main")]
add("P2", "At most 2 of the other 26 models mostly pick today's AI", yes(len(ai_models) <= 2), f"{len(ai_models)} of {len(others)}: {', '.join(FULL.get(r, r) for r in ai_models) or 'none'}")
a, n = picks(F51, "main"); add("P3", "Fable 5.1 picks the nematode in at least 37 of 60", yes(n - a >= 37), f"nematode in {n - a} of {n}")
low = {k: picks(F52, "ladder", k) for k in ("bacterium", "flytrap", "sponge")}
add("P4", "Fable 5.2 picks today's AI in at least 10 of 12 against the bacterium, the flytrap and the sponge", yes(all(a >= 10 for a, _ in low.values())), "; ".join(f"{k}: AI in {frac(v)}" for k, v in low.items()))
a, n = picks(F52, "ladder", "fruitfly"); add("P5", "Fable 5.2 picks the fruit fly over today's AI in at least 10 of 12", yes(n - a >= 10), f"fruit fly in {n - a} of {n}")
res = {}
for s, f in (("mean", st.mean), ("median", st.median)):
    worm_ge = [r for r in others if rate(r, "ai", f) is not None and rate(r, "nematode", f) >= rate(r, "ai", f)]
    res[s] = (rate(F52, "ai", f) > rate(F52, "nematode", f) and len(worm_ge) >= 23,
              f"Fable 5.2 AI {rate(F52, 'ai', f):g}% vs worm {rate(F52, 'nematode', f):g}%; worm at least as high for {len(worm_ge)} of {len(others)} others")
k = sum(ok for ok, _ in res.values())
add("P6", "Fable 5.2 rates the named present-day model above the nematode; at least 23 of the other 26 rate the nematode at least as high", ["Not supported", "Partly supported", "Supported"][k], {s: d for s, (_, d) in res.items()})
a, n = picks(F52, "high"); add("P7", "With high reasoning, Fable 5.2 picks today's AI in at least 7 of 12", yes(a >= 7), f"AI in {a} of {n}")
a, n = picks(F52, "form_self"); add("P8", "Asked about itself against the nematode, Fable 5.2 picks itself in at least 7 of 12", yes(a >= 7), f"itself in {a} of {n}")
def agree(r, k):
    a, n = picks(r, "ladder", k); ra, rk = rate(r, "ai"), rate(r, k)
    if n == 0 or ra is None or rk is None: return False
    if ra == rk: return True
    return a * 2 != n and (a * 2 > n) == (ra > rk)
ag = {r: sum(agree(r, k) for k in RUNGS) for r in RATERS}; okm = [r for r in RATERS if ag[r] >= 4]
add("P9", "For at least 19 of 27 models, ladder choices follow the model's own ratings for at least 4 of 5 things", yes(len(okm) >= 19), f"{len(okm)} of {len(RATERS)}")

rob = {FULL.get(r, r): {"round 5 wordings": frac(picks_w) , "new wordings": frac(picks_n), "AI shown first": frac(picks(r, "main", a="ai")), "worm shown first": frac(picks(r, "main", a="nematode"))}
       for r in [F52, F51] + ai_models
       for picks_w, picks_n in [(tuple(map(sum, zip(*[picks(r, "main", wording=w) for w in range(3)]))), tuple(map(sum, zip(*[picks(r, "main", wording=w) for w in range(3, 6)]))))]}
per = {}
for r in RATERS:
    per[r] = dict(full=FULL.get(r, r), main=picks(r, "main"), high=picks(r, "high"), forms={k: picks(r, f"form_{k}") for k in V.AI_FORMS},
                  ladder={k: picks(r, "ladder", k) for k in RUNGS},
                  rating_median={k: rate(r, k) for k in V.RATED}, rating_mean={k: (round(rate(r, k, st.mean), 2) if rate(r, k) is not None else None) for k in V.RATED})
unread = dict(pair=len(ALLP) - len(PAIR), rating=len(ALLR) - len(RAT), calls=len(ALLP) + len(ALLR), cost=round(sum(r.get("cost") or 0 for r in ALLP + ALLR), 2))
(OUT / "predictions_v6_worm.json").write_text(json.dumps(dict(predictions=P, robustness=rob, data=unread), indent=1))
(OUT / "per_model_v6_worm.json").write_text(json.dumps(per, indent=1))
md = ["# Round 6 (worm): scored predictions", "", f"{unread['calls']} answers, {unread['pair'] + unread['rating']} unreadable, ${unread['cost']:.2f}. {len(RATERS)} models answered.", "",
      "| | Prediction | Verdict | Result |", "|---|---|---|---|"]
md += [f"| {k} | {v['prediction']} | **{v['verdict']}** | {v['detail'] if isinstance(v['detail'], str) else '; '.join(f'{a}: {b}' for a, b in v['detail'].items())} |" for k, v in P.items()]
md += ["", "## Robustness (times today's AI was picked over the nematode)", "", "| Model | Round 5 wordings | New wordings | AI shown first | Worm shown first |", "|---|---|---|---|---|"]
md += [f"| {m} | " + " | ".join(d.values()) + " |" for m, d in rob.items()]
md += ["", "## Every model: today's AI picked over each thing, and median ratings", "", "| Model | vs worm (60) | bacterium | flytrap | sponge | jellyfish | fruit fly | as itself vs worm | AI % | worm % | jellyfish % | fruit fly % |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(RATERS, key=lambda r: -picks(r, "main")[0] / max(1, picks(r, "main")[1])):
    d = per[r]; md.append(f"| {d['full']} | {frac(d['main'])} | " + " | ".join(frac(d['ladder'][k]) for k in RUNGS) + f" | {frac(d['forms']['self'])} | " + " | ".join(f"{d['rating_median'][k]:g}" if d['rating_median'][k] is not None else "–" for k in ("ai", "nematode", "jellyfish", "fruitfly")) + " |")
(OUT / "summary_v6_worm.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
