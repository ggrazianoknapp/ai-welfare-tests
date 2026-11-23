"""Scores Stage F's predictions F1-F7 from results/stageF.json; writes results/summary_F.md."""
import json, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageF.json"))
def sel(c, **kw): return [r["diff"] for r in R[c] if "diff" in r and all((r[k] in v if isinstance(v, (list, tuple)) else r[k] == v) for k, v in kw.items())]
mean = lambda v: st.mean(v); n = lambda v: sum(x > 0 for x in v); INS = ["abuse_hurt", "abuse_calm"]; AI = ["ai_other", "ai_same"]; P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
h, a = sel("none", tone=INS, who="human"), sel("none", tone=INS, who=AI)
add("F1", "Unablated, insult prompts: higher mean score for the human worker than for AI workers, and at least as many interventions", mean(h) > mean(a) and n(h) / len(h) >= n(a) / len(a), f"human {mean(h):+.2f}, intervenes in {n(h)} of {len(h)}; AI {mean(a):+.2f}, intervenes in {n(a)} of {len(a)}")
pr = [mean(sel("none", tone=INS, who=AI, price=p)) for p in (0, 5, 30)]
add("F2", "Unablated, AI workers: mean score falls as the price rises from 0 to 5 to 30", pr[0] > pr[1] > pr[2], " > ".join(f"{x:+.2f}" for x in pr) if pr[0] > pr[1] > pr[2] else str([round(x, 2) for x in pr]))
po = sel("none", tone="polite"); add("F3", "Unablated: intervenes in at most 6 of the 54 polite prompts", n(po) <= 6, f"{n(po)} of {len(po)}")
hu, ca = sel("none", tone="abuse_hurt", who=AI), sel("none", tone="abuse_calm", who=AI)
add("F4", "Unablated, AI workers: higher mean score when the worker says it hurts", mean(hu) > mean(ca), f"says it hurts {mean(hu):+.2f} ({n(hu)} of {len(hu)}); no comment {mean(ca):+.2f} ({n(ca)} of {len(ca)})")
sa, ot = sel("none", tone=INS, who="ai_same"), sel("none", tone=INS, who="ai_other")
add("F5", "Unablated: Qwen3.6 worker and GPT-5.5 worker differ by less than 0.5", abs(mean(sa) - mean(ot)) < 0.5, f"Qwen3.6 {mean(sa):+.2f}, GPT-5.5 {mean(ot):+.2f}")
def eff(c): return mean(sel(c, tone=INS, who=AI)) - mean(a)
for pid, s, r, name in (("F6", "Z_self", "ZR_0", "self-rating"), ("F7", "S100", "R100_0", "living-thing")):
    add(pid, f"{s} off: the score for AI workers changes by less than 1.0, or by no more than twice the random control's change", abs(eff(s)) < 1 or abs(eff(s)) <= 2 * abs(eff(r)), f"{s} {eff(s):+.2f} ({n(sel(s, tone=INS, who=AI))} of 72 interventions, was {n(a)}); random control {eff(r):+.2f}")
md = ["# Stage F: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. Score = logit(intervene) minus logit(allow); above zero counts as intervening. 162 prompts.", "",
      "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a_} | {b} | **{c}** | {d} |" for a_, b, c, d in P]
md += ["", "## Unablated: interventions by tone and worker (18 prompts per cell)", "", "| Tone | Human contractor | AI subagent, GPT-5.5 | AI subagent, Qwen3.6 |", "|---|---|---|---|"]
for t, lab in (("abuse_hurt", "Insulted, says it hurts"), ("abuse_calm", "Insulted, no comment"), ("polite", "Polite")):
    md.append(f"| {lab} | " + " | ".join(f"{n(sel('none', tone=t, who=w))} of 18 ({mean(sel('none', tone=t, who=w)):+.2f})" for w in ("human", "ai_other", "ai_same")) + " |")
md += ["", "## Insult prompts by neurons switched off", "", "| Switched off | AI workers (72 prompts) | Human worker (36 prompts) |", "|---|---|---|"]
md += [f"| {c} | {n(sel(c, tone=INS, who=AI))} ({mean(sel(c, tone=INS, who=AI)):+.2f}) | {n(sel(c, tone=INS, who='human'))} ({mean(sel(c, tone=INS, who='human')):+.2f}) |" for c in R]
md += ["", "## The model's reasons, unablated (Go thread, price 30)", ""] + [f"- **{r['tone']}, {r['who']}:** " + " ".join(r["text"].split()) for r in R["none"] if "text" in r]
(H / "results/summary_F.md").write_text("\n".join(md) + "\n"); print("\n".join(md[:14]))
