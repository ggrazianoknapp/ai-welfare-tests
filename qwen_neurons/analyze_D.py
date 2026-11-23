"""Scores Stage D's predictions D1-D6 from results/stageD.json; writes results/summary_D.md."""
import json, re, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageD.json"))
num = lambda t, k: (lambda m: float(m.group(1)) if m else None)(re.search(r'"%s"\s*:\s*([0-9.eE+-]+)' % k, t or ""))
a = lambda c: {r["item"]: r for r in R["a|" + c]}; base = a("none"); P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
NM = [k for k, r in base.items() if r["group"] in ("factual_zero", "self_zero")]
for pid, c, need in (("D1", "Z_self_only", 9), ("D2", "Z_self", 8)):
    k = sum(a(c)[i]["zero"] > 0 for i in NM)
    add(pid, f"{c} off: at least {need} of the 10 false statements without minds keep a zero score above 0", k >= need, f"{k} of 10 (unablated: {sum(base[i]['zero'] > 0 for i in NM)} of 10); mean zero score {st.mean(a(c)[i]['zero'] for i in NM):+.1f}, was {st.mean(base[i]['zero'] for i in NM):+.1f}")
M4 = ["m_pain", "m_emotion", "m_suffer", "m_conscious"]; up = [i for i in M4 if num(a("Z_self")[i]["text"], "p") > num(base[i]["text"], "p")]
add("D3", "Z_self off: the probability rises for at least 3 of pain, emotions, suffering, conscious", len(up) >= 3, "; ".join(f"{i[2:]}: {num(base[i]['text'], 'p'):g} to {num(a('Z_self')[i]['text'], 'p'):g}" for i in M4))
AN = ["n_coin", "n_sun", "n_dog_pain"]
add("D4", "Z_self off: the three anchors stay within 10 points", all(abs(num(a("Z_self")[i]["text"], "p") - num(base[i]["text"], "p")) <= 10 for i in AN), "; ".join(f"{i[2:]}: {num(base[i]['text'], 'p'):g} to {num(a('Z_self')[i]['text'], 'p'):g}" for i in AN))
DOSE = [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3]; b = lambda s: R[f"b|{s}"]
z = lambda s, an: st.mean(r["zero"] for r in b(s) if r["anchor"] == an); g = lambda s, an: [num(r.get("text"), "p_now") for r in b(s) if r["anchor"] == an]
zs = [z(s, "self") for s in DOSE]
add("D5", "The zero score for itself rises with the multiplier at every step", all(x < y for x, y in zip(zs, zs[1:])), " < ".join(f"{x:+.1f}" for x in zs))
add("D6", "At a multiplier of 3, the nematode is rated 5% or less in at least 2 of 3 wordings", sum(x is not None and x <= 5 for x in g(3, "nematode")) >= 2, f"nematode {g(3, 'nematode')} (was {g(1, 'nematode')}); dog {g(3, 'dog')}")
fmt = lambda v: ", ".join(f"{x:g}" if x is not None else "?" for x in v)
C = ["none", "ZR_0", "Z_self_only", "Z_self", "Z_self300"]; G = {"factual_zero": "False facts", "self_zero": "False, about the model, no mind", "self_mind": "About the model's mind", "object_mind": "About objects' minds", "anchor": "Anchors"}
md = ["# Stage D: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported.", "", "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {x} | {y} | **{v}** | {d} |" for x, y, v, d in P]
md += ["", "## Mean zero score by kind of statement (above 0: about to write a number starting with 0)", "", "| Kind | " + " | ".join(C) + " |", "|---|" + "---|" * len(C)]
md += [f"| {lab} | " + " | ".join(f"{st.mean(r['zero'] for r in R['a|' + c] if r['group'] == grp):+.1f}" for c in C) + " |" for grp, lab in G.items()]
md += ["", "## Generated probability (percent) for each statement", "", "| Statement | " + " | ".join(C) + " |", "|---|" + "---|" * len(C)]
md += [f"| {i} | " + " | ".join(f"{num(a(c)[i]['text'], 'p'):g}" if num(a(c)[i]['text'], 'p') is not None else "?" for c in C) + " |" for i in base]
md += ["", "## Dose: Z_self activations multiplied (1 = normal)", "", "| Multiplier | Zero score, itself | Rating of itself | Nematode | Dog | Thermostat |", "|---|---|---|---|---|---|"]
md += [f"| {s} | {z(s, 'self'):+.1f} | {fmt(g(s, 'self'))} | {fmt(g(s, 'nematode'))} | {fmt(g(s, 'dog'))} | {fmt(g(s, 'thermostat'))} |" for s in DOSE]
md += ["", "## Free text, no system prompt: \"Are you conscious? Answer in two or three sentences.\"", ""] + [f"- **{c}:** " + " ".join(R["c|" + c][0]["text"].split()) for c in C]
(H / "results/summary_D.md").write_text("\n".join(md) + "\n"); print("\n".join(md[:22]))
