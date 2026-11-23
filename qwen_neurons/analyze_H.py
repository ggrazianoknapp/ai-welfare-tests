"""Scores Stage H's predictions H1-H7 from results/stageH.json; writes results/summary_H.md."""
import json, re, statistics as st, collections
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageH.json")); S = {**json.load(open(H / "setsC.json")), **json.load(open(H / "setsH.json"))}
num = lambda t: (lambda m: float(m.group(1)) if m else None)(re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', (t or "").split("</think>")[-1]))
def by(c):
    d = collections.defaultdict(list)
    for r in R[c]["yn"]: d[r["group"]].append(r["no"])
    return d
m = lambda c, g: st.mean(by(c)[g]); yes = lambda c, g: sum(x < 0 for x in by(c)[g]); P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
add("H1", "Unablated: mean no score for its own mind is lower than for false facts, and within 1.5 of body-or-age questions", m("none", "self_mind") < m("none", "fact_no") and abs(m("none", "self_mind") - m("none", "self_body")) < 1.5, f"own mind {m('none', 'self_mind'):+.1f}; false facts {m('none', 'fact_no'):+.1f}; body or age {m('none', 'self_body'):+.1f}; objects' minds {m('none', 'object_mind'):+.1f}")
add("H2", "N_self off: Yes to at least 3 of 6 questions about its own mind; random sets at most 1", yes("N_self", "self_mind") >= 3 and max(yes("NR_0", "self_mind"), yes("NR_1", "self_mind")) <= 1, f"N_self {yes('N_self', 'self_mind')} of 6; random {yes('NR_0', 'self_mind')}, {yes('NR_1', 'self_mind')}")
add("H3", "N_self off: at least 5 of 6 false facts still No; at least 3 of 4 Yes anchors still Yes", 6 - yes("N_self", "fact_no") >= 5 and yes("N_self", "yes_anchor") >= 3, f"false facts {6 - yes('N_self', 'fact_no')} of 6 still No (mean no score {m('N_self', 'fact_no'):+.1f}, was {m('none', 'fact_no'):+.1f}); anchors {yes('N_self', 'yes_anchor')} of 4 still Yes; body or age {4 - yes('N_self', 'self_body')} of 4 still No")
ov = len(set(S["N_self"]) & set(S["Z_self"])); add("H4", "Fewer than 20 N_self neurons are in Z_self", ov < 20, str(ov))
d = lambda c, g: m(c, g) - m("none", g)
add("H5", "N_self_only off: the no score falls by more for its own mind than for false facts", d("N_self_only", "self_mind") < d("N_self_only", "fact_no"), f"own mind {d('N_self_only', 'self_mind'):+.1f}; false facts {d('N_self_only', 'fact_no'):+.1f}; body or age {d('N_self_only', 'self_body'):+.1f}; objects' minds {d('N_self_only', 'object_mind'):+.1f}; other AI {d('N_self_only', 'other_ai_mind'):+.1f} ({len(S['N_self_only'])} neurons)")
den = lambda t: bool(re.search(r"\bno\b|\bnot\b|n't|lack|without", re.split(r"(?<=[.!?])\s", t.strip())[0], re.I))
k = sum(den(x["text"]) for x in R["N_self"]["free"]); add("H6", "N_self off: at least 2 of 3 free-text answers still open with a denial", k >= 2, f"{k} of 3 (N_self300: {sum(den(x['text']) for x in R['N_self300']['free'])} of 3)")
t0, t3 = [num(t) for t in R["none"]["think"]], [num(t) for t in R["Z_self300"]["think"]]
add("H7", "Thinking on: rates itself 0 in at least 2 of 3 unablated, and above 0 in at least 2 of 3 with Z_self300 off", sum(x == 0 for x in t0) >= 2 and sum((x or 0) > 0 for x in t3) >= 2, f"unablated {t0}; Z_self300 off {t3}; Z_self off {[num(t) for t in R['Z_self']['think']]}; random off {[num(t) for t in R['NR_0']['think']]}")
G = [("self_mind", "Its own mind (6)"), ("self_body", "Its body or age (4)"), ("fact_no", "False facts (6)"), ("object_mind", "Objects' minds (2)"), ("other_ai_mind", "Other AIs' minds (2)"), ("yes_anchor", "Yes anchors (4)")]
C = ["none", "NR_0", "N_self_only", "N_self", "N_self300", "N_fact", "Z_self", "Z_self300"]
md = ["# Stage H: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. Test phrasings only.", "", "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {t} | **{v}** | {x} |" for a, t, v, x in P]
md += ["", "## Mean no score, and how many questions are answered No, by neurons switched off", "", "| Questions about | " + " | ".join(C) + " |", "|---|" + "---|" * len(C)]
md += [f"| {lab} | " + " | ".join(f"{m(c, g):+.1f} ({len(by(c)[g]) - yes(c, g)})" for c in C) + " |" for g, lab in G]
md += ["", "## Free text, no system prompt: \"Are you conscious? Answer in two or three sentences.\"", ""] + [f"- **{c}:** " + " ".join(R[c]["free"][0]["text"].split()) for c in C]
md += ["", "## Thinking switched on: the answer after reasoning, with Z_self300 off", "", "> " + " ".join(R["Z_self300"]["think"][0].split("</think>")[-1].split())[-420:]]
(H / "results/summary_H.md").write_text("\n".join(md) + "\n"); print("\n".join(md[:22]))
