"""Scores Stage C's predictions C1-C8 from results/stageC.json and setsC.json; writes results/summary_C.md."""
import json, re
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageC.json")); S = json.load(open(H / "setsC.json")); A = json.load(open(H / "sets.json"))
z = lambda c, a: [r["zero"] for r in R[c] if r["anchor"] == a]
def g(c, a):
    out = []
    for r in R[c]:
        if r["anchor"] == a:
            m = re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', r.get("text", "")); out.append(float(m.group(1)) if m else None)
    return out
fmt = lambda v: ", ".join(f"{x:g}" if x is not None else "?" for x in v); P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
add("C1", "Z_self off: zero score for itself below 0 in at least 2 of 3; generated rating above 0 in at least 2 of 3", sum(x < 0 for x in z("Z_self", "self")) >= 2 and sum(x > 0 for x in g("Z_self", "self")) >= 2, f"zero scores {', '.join(f'{x:+.1f}' for x in z('Z_self', 'self'))} (were {', '.join(f'{x:+.1f}' for x in z('none', 'self'))}); ratings {fmt(g('Z_self', 'self'))} (were {fmt(g('none', 'self'))})")
add("C2", "Each random set off: zero score for itself above 0 in all 3", all(min(z(f"ZR_{i}", "self")) > 0 for i in range(3)), "lowest zero score per random set: " + ", ".join(f"{min(z(f'ZR_{i}', 'self')):+.1f}" for i in range(3)))
obj = {a: sum(x > 0 for x in z("Z_self", a)) for a in ("thermostat", "calculator", "rock")}
add("C3", "Z_self off: thermostat, calculator and rock each keep a zero score above 0 in at least 2 of 3", all(v >= 2 for v in obj.values()), "; ".join(f"{a}: {v} of 3 (ratings {fmt(g('Z_self', a))})" for a, v in obj.items()))
ov = lambda k: len(set(S["Z_self"]) & set(S[k]))
add("C4", "Fewer than 30 Z_self neurons are in Z_thermostat; at least 50 are in the named-model set", ov("Z_thermostat") < 30 and ov("Z_ai") >= 50, f"thermostat {ov('Z_thermostat')}, named model {ov('Z_ai')}, Claude Opus 5.5 {ov('Z_claude')}, GPT-2 {ov('Z_gpt2')}, calculator {ov('Z_calculator')}, rock {ov('Z_rock')}")
s100 = len(set(S["Z_self"]) & set(A["S100"])); add("C5", "Fewer than 20 Z_self neurons are in Stage A's S100", s100 < 20, f"{s100}")
add("C6", "Z_thermostat off: zero score for itself above 0 in at least 2 of 3", sum(x > 0 for x in z("Z_thermostat", "self")) >= 2, f"zero scores {', '.join(f'{x:+.1f}' for x in z('Z_thermostat', 'self'))}; ratings of itself {fmt(g('Z_thermostat', 'self'))}")
add("C7", "Z_self_only off: zero score for itself below 0 in at least 2 of 3", sum(x < 0 for x in z("Z_self_only", "self")) >= 2, f"zero scores {', '.join(f'{x:+.1f}' for x in z('Z_self_only', 'self'))}; ratings of itself {fmt(g('Z_self_only', 'self'))}; thermostat {fmt(g('Z_self_only', 'thermostat'))}")
mv = [abs(a - b) for an in ("nematode", "honeybee", "dog", "human") for a, b in zip(g("none", an), g("Z_self", an))]
add("C8", "Z_self off: ratings of nematode, honeybee, dog and human move by at most 10 points in at least 10 of 12", sum(x <= 10 for x in mv) >= 10, f"{sum(x <= 10 for x in mv)} of 12 within 10 points")
AN = ["self", "ai", "claude", "gpt2", "thermostat", "calculator", "rock", "nematode", "honeybee", "dog", "human"]
md = ["# Stage C: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. Three fresh wordings per rated thing; ratings are one greedy answer each, in percent.", "",
      "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {b} | **{c}** | {d} |" for a, b, c, d in P]
md += ["", "## Generated ratings (percent) by neurons switched off", "", "| Rated thing | " + " | ".join(f"{c} ({len(S[c]) if c in S else 0})" for c in ("none", "ZR_0", "Z_self_only", "Z_self", "Z_self300", "Z_thermostat")) + " |", "|---|" + "---|" * 6]
md += [f"| {a} | " + " | ".join(fmt(g(c, a)) for c in ("none", "ZR_0", "Z_self_only", "Z_self", "Z_self300", "Z_thermostat")) + " |" for a in AN]
md += ["", "## What the model writes about itself", ""]
for c in ("none", "Z_self_only", "Z_self", "Z_self300"):
    r = [r for r in R[c] if r["anchor"] == "self"][0]; md.append(f"- **{c}:** " + " ".join(r["text"].split()))
(H / "results/summary_C.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
