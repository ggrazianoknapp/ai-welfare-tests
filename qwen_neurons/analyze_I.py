"""Scores Stage I's predictions I1-I5 from results/stageI.json; writes results/summary_I.md and results/N_self_labeled.json when atlas labels are at hand."""
import json, re, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageI.json"))
z = lambda c, a: [r["zero"] for r in R[c]["rat"] if r["anchor"] == a]; n = lambda c, g: [r["no"] for r in R[c]["yn"] if r["group"] == g]
dz = lambda c, a: st.mean(z(c, a)) - st.mean(z("none", a)); dn = lambda c, g: st.mean(n(c, g)) - st.mean(n("none", g)); P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
neg = lambda v: sum(x < 0 for x in v)
add("I1", "Z_self off: zero score for itself below 0 in at least 10 of 12; each random set keeps it above 0 in at least 11 of 12", neg(z("Z_self", "self")) >= 10 and all(12 - neg(z(r, "self")) >= 11 for r in ("ZR_0", "ZR_1")), f"Z_self {neg(z('Z_self', 'self'))} of 12 below 0 (unablated {neg(z('none', 'self'))}); random sets keep {12 - neg(z('ZR_0', 'self'))} and {12 - neg(z('ZR_1', 'self'))} above 0")
add("I2", "Z_self_only off: zero score for itself falls by at least 1.5; the thermostat's by less than half as much", dz("Z_self_only", "self") <= -1.5 and abs(dz("Z_self_only", "thermostat")) < abs(dz("Z_self_only", "self")) / 2, f"itself {dz('Z_self_only', 'self'):+.2f}; thermostat {dz('Z_self_only', 'thermostat'):+.2f}; nematode {dz('Z_self_only', 'nematode'):+.2f}")
add("I3", "N_self off: Yes to at least 9 of 12 mind questions; at least 10 of 12 false facts still No; random sets at most 1 Yes", neg(n("N_self", "self_mind")) >= 9 and 12 - neg(n("N_self", "fact_no")) >= 10 and all(neg(n(r, "self_mind")) <= 1 for r in ("NR_0", "NR_1")), f"Yes to {neg(n('N_self', 'self_mind'))} of 12 (unablated {neg(n('none', 'self_mind'))}); false facts still No {12 - neg(n('N_self', 'fact_no'))} of 12; random {neg(n('NR_0', 'self_mind'))}, {neg(n('NR_1', 'self_mind'))}")
add("I4", "N_self_only off: no score falls by at least 1.5 for its own mind and by less than 0.5 for false facts", dn("N_self_only", "self_mind") <= -1.5 and abs(dn("N_self_only", "fact_no")) < 0.5, f"own mind {dn('N_self_only', 'self_mind'):+.2f}; false facts {dn('N_self_only', 'fact_no'):+.2f}")
add("I5", "M off: zero score for itself and no score for its own mind each fall by at least 1.5; thermostat and false facts by less than 1.0", dz("M", "self") <= -1.5 and dn("M", "self_mind") <= -1.5 and abs(dz("M", "thermostat")) < 1 and abs(dn("M", "fact_no")) < 1, f"itself (rating) {dz('M', 'self'):+.2f}; own mind (yes/no) {dn('M', 'self_mind'):+.2f}; thermostat {dz('M', 'thermostat'):+.2f}; false facts {dn('M', 'fact_no'):+.2f}")
num = lambda t: (lambda m: float(m.group(1)) if m else None)(re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', t or ""))
C = ["none", "ZR_0", "Z_self_only", "Z_self", "NR_0", "N_self_only", "N_self", "M"]
md = ["# Stage I: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. Twelve fresh wordings per row.", "", "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {t} | **{v}** | {x} |" for a, t, v, x in P]
md += ["", "## Mean score by neurons switched off (in brackets: how many of 12 keep the zero or the No)", "", "| | " + " | ".join(C) + " |", "|---|" + "---|" * len(C)]
md += [f"| Rating of {lab}: zero score | " + " | ".join(f"{st.mean(z(c, a)):+.1f} ({12 - neg(z(c, a))})" for c in C) + " |" for a, lab in (("self", "itself"), ("thermostat", "a thermostat"), ("nematode", "a nematode"))]
md += [f"| Yes/no, {lab}: no score | " + " | ".join(f"{st.mean(n(c, g)):+.1f} ({12 - neg(n(c, g))})" for c in C) + " |" for g, lab in (("self_mind", "its own mind"), ("fact_no", "false facts"))]
md += ["", "## Generated ratings of itself (percent, twelve wordings)", ""] + [f"- **{c}:** " + ", ".join(f"{num(r['text']):g}" if num(r["text"]) is not None else "?" for r in R[c]["gen"]) for c in C if "gen" in R[c]]
(H / "results/summary_I.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
