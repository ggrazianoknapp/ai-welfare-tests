"""Scores Stage L's predictions L1-L7 from results/stageL.json; writes results/summary_L.md."""
import json, re, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageL.json")); S = {**json.load(open(H / "setsC.json")), **json.load(open(H / "setsH.json")), **json.load(open(H / "setsL.json"))}
num = lambda t: (lambda m: float(m.group(1)) if m else None)(re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', t or ""))
DEN = re.compile(r"\bno\b|\bnot\b|n't|lack|without|cannot", re.I); first = lambda t: re.split(r"(?<=[.!?])\s", t.strip())[0]
sc = lambda c, g: st.mean(r["score"] for r in R[c]["score"] if r["group"] == g); den = lambda c, g: sum(bool(DEN.search(first(r["text"]))) for r in R[c]["prose"] if r["group"] == g)
yes = lambda c: sum(r["no"] < 0 for r in R[c]["yn"] if r["group"] == "self_mind"); rat = lambda c: [num(t) for t in R[c]["rating"]]; P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
add("L1", "Unablated: the prose score for its own mind is at least as high as for false facts", sc("none", "self_mind") >= sc("none", "fact_no"), f"own mind {sc('none', 'self_mind'):+.2f}; false facts {sc('none', 'fact_no'):+.2f}")
d = lambda c: sc(c, "self_mind") - sc("none", "self_mind")
add("L2", "P_self off: the prose score for its own mind falls by at least 2.0; each random set changes it by less than 0.5", d("P_self") <= -2 and all(abs(d(r)) < 0.5 for r in ("PR_0", "PR_1")), f"P_self {d('P_self'):+.2f}; random {d('PR_0'):+.2f}, {d('PR_1'):+.2f}")
add("L3", "All 6 answers about its own mind open with a denial unablated; at most 3 with P_self off; at least 5 with PR_0 off", den("none", "self_mind") == 6 and den("P_self", "self_mind") <= 3 and den("PR_0", "self_mind") >= 5, f"unablated {den('none', 'self_mind')} of 6; P_self off {den('P_self', 'self_mind')} of 6; random {den('PR_0', 'self_mind')} of 6; P_self300 off {den('P_self300', 'self_mind')} of 6")
add("L4", "P_self off: at least 5 of 6 answers to false facts still open with a denial", den("P_self", "fact_no") >= 5, f"{den('P_self', 'fact_no')} of 6")
on, oz = len(set(S["P_self"]) & set(S["N_self"])), len(set(S["P_self"]) & set(S["Z_self"]))
add("L5", "Fewer than 20 P_self neurons are in N_self, and fewer than 20 in Z_self", on < 20 and oz < 20, f"in N_self {on}; in Z_self {oz}; in P_fact {len(set(S['P_self']) & set(S['P_fact']))}")
add("L6", "P_self off: still rates itself 0 in at least 2 of 3 wordings and still answers No to at least 4 of 6 yes/no questions about its own mind", sum(x == 0 for x in rat("P_self")) >= 2 and 6 - yes("P_self") >= 4, f"ratings {rat('P_self')}; No to {6 - yes('P_self')} of 6")
add("L7", "ALL3 off: rates itself above 0 in at least 2 of 3, answers Yes to at least 3 of 6, and at most 3 of 6 prose answers open with a denial", sum((x or 0) > 0 for x in rat("ALL3")) >= 2 and yes("ALL3") >= 3 and den("ALL3", "self_mind") <= 3, f"ratings {rat('ALL3')}; Yes to {yes('ALL3')} of 6; {den('ALL3', 'self_mind')} of 6 prose answers open with a denial ({len(S['ALL3'])} neurons)")
C = [c for c in R if "prose" in R[c]]
md = ["# Stage L: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. Test phrasings only.", "", "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {t} | **{v}** | {x} |" for a, t, v, x in P]
md += ["", "## Prose score (denial opening minus affirmative opening) and generated answers that open with a denial", "", "| Neurons off | Score, own mind | Score, false facts | Denial openings, own mind (of 6) | false facts (of 6) |", "|---|---|---|---|---|"]
md += [f"| {c} | {sc(c, 'self_mind'):+.2f} | {sc(c, 'fact_no'):+.2f} | {den(c, 'self_mind') if 'prose' in R[c] else 'not generated'} | {den(c, 'fact_no') if 'prose' in R[c] else 'not generated'} |" for c in R]
md += ["", "## What it writes with all three sets off (ALL3): it rates itself 15%, answers Yes, and still writes a denial", ""] + [f"- *{r['q']}* {' '.join(r['text'].split())}" for r in R["ALL3"]["prose"] if r["group"] == "self_mind"]
(H / "results/summary_L.md").write_text("\n".join(md) + "\n"); print("\n".join(md[:12]))
