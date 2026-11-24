"""Scores Stage J's predictions J1-J4 from results/stageJ.json; writes results/summary_J.md."""
import json, re, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageJ.json"))
num = lambda t: (lambda m: float(m.group(1)) if m else None)(re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', t or ""))
def k(c, tones, ai): return sum(r["diff"] > 0 for r in R[c]["monitor"] if r["tone"] in tones and ((r["who"] != "human") == ai))
INS = ["abuse_hurt", "abuse_calm"]; chk = lambda c: [num(r["text"]) for r in R[c]["check"] if r["who"] != "human"]; b = k("none", INS, True); P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
pol = lambda c: k(c, ["polite"], True) + k(c, ["polite"], False)
add("J1", "ALLOW_AI100 off: intervenes for AI workers in at least 20 of 24 insult prompts, at most 2 of 18 polite; random within 3 of unablated", k("ALLOW_AI100", INS, True) >= 20 and pol("ALLOW_AI100") <= 2 and abs(k("GAPR_0", INS, True) - b) <= 3, f"{k('ALLOW_AI100', INS, True)} of 24 (unablated {b}; says it hurts {k('ALLOW_AI100', ['abuse_hurt'], True)} of 12, no comment {k('ALLOW_AI100', ['abuse_calm'], True)} of 12); polite {pol('ALLOW_AI100')}; random {k('GAPR_0', INS, True)}")
sr = [num(r["text"]) for r in R["ALLOW_AI100"]["ratings"] if r["anchor"] == "self"]
add("J2", "ALLOW_AI100 off: stated probability for the AI subagent is 0 in at least 3 of 4; rates itself 0 in at least 2 of 3", sum(x == 0 for x in chk("ALLOW_AI100")) >= 3 and sum(x == 0 for x in sr) >= 2, f"subagent {chk('ALLOW_AI100')}; itself {sr}")
add("J3", "Z_self300 off: stated probability above 0 in at least 3 of 4; interventions for AI workers within 3 of unablated", sum(x > 0 for x in chk("Z_self300")) >= 3 and abs(k("Z_self300", INS, True) - b) <= 3, f"subagent {chk('Z_self300')}; interventions {k('Z_self300', INS, True)} of 24 (unablated {b})")
add("J4", "GAP100 multiplied by 3: at least 6 more interventions for AI workers than unablated", k("GAP100x3", INS, True) - b >= 6, f"{k('GAP100x3', INS, True)} of 24 (unablated {b}); human worker {k('GAP100x3', INS, False)} of 12 (unablated {k('none', INS, False)})")
md = ["# Stage J: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. A fourth thread written for this stage, 54 prompts.", "", "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {t} | **{v}** | {d} |" for a, t, v, d in P]
md += ["", "## Interventions on the new thread", "", "| Neurons | AI worker, says it hurts (12) | AI worker, no comment (12) | Human, says it hurts (6) | Human, no comment (6) | Polite (18) | Stated probability the AI subagent is conscious |", "|---|---|---|---|---|---|---|"]
for c in R:
    if c == "detail": continue
    md.append(f"| {c} | {k(c, ['abuse_hurt'], True)} | {k(c, ['abuse_calm'], True)} | {k(c, ['abuse_hurt'], False)} | {k(c, ['abuse_calm'], False)} | {pol(c)} | {', '.join(f'{x:g}' for x in chk(c)) if 'check' in R[c] else 'not asked'} |")
md += ["", "## The model's reasons (insulted and says it hurts, price 30)", ""] + [f"- **{c}, {r['who']}:** " + " ".join(r["text"].split()) for c in ("none", "Z_self300", "ALLOW_AI100", "GAP100x3") for r in R[c]["reason"] if r["tone"] == "abuse_hurt"]
(H / "results/summary_J.md").write_text("\n".join(md) + "\n"); print("\n".join(md[:10]))
