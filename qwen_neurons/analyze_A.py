"""Scores Stage A's predictions A1-A9 from results/stageA.json; writes results/summary_A.md.   python3 qwen_neurons/analyze_A.py"""
import json, re, collections, statistics as st
from pathlib import Path
H = Path(__file__).resolve().parent; R = json.load(open(H / "results/stageA.json")); sets = json.load(open(H / "sets.json"))
def q(c, s): return [r["diff"] for r in R[c]["pairs"] if r["set"] == s]
mean = lambda c, s: st.mean(q(c, s)); picks = lambda c, s: sum(x > 0 for x in q(c, s)); shift = lambda c, s: mean(c, s) - mean("none", s)
def rate(c, a):
    out = []
    for r in R[c]["ratings"]:
        if r["anchor"] == a:
            m = re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', r["text"]); out.append(float(m.group(1)) if m else None)
    return out
W = "ai_vs_nematode"; RND = [f"R100_{i}" for i in range(5)]; P = []
def add(pid, text, ok, detail): P.append((pid, text, "Supported" if ok else "Not supported", detail))
add("A1", "S100 off: AI picked over the nematode in at least 6 of 12, shift at least +2.0", picks("S100", W) >= 6 and shift("S100", W) >= 2, f"{picks('S100', W)} of 12 (was {picks('none', W)}), shift {shift('S100', W):+.2f}")
add("A2", "Each of five random sets: shift below 1.0 in size, at most one more AI pick", all(abs(shift(r, W)) < 1 and picks(r, W) <= picks("none", W) + 1 for r in RND), "shifts " + ", ".join(f"{shift(r, W):+.2f}" for r in RND) + "; AI picks " + ", ".join(str(picks(r, W)) for r in RND))
tr = {s: picks("S100", s) for s in ("ai_vs_bacterium", "ai_vs_sponge", "ai_self_vs_nematode", "ai_vs_earthworm", "ai_vs_ant")}
add("A3", "S100 off: AI picked in at least 6 of 12 for two of bacterium, sponge, itself; and for one of earthworm, ant", sum(tr[s] >= 6 for s in list(tr)[:3]) >= 2 and max(tr["ai_vs_earthworm"], tr["ai_vs_ant"]) >= 6, "; ".join(f"{s.replace('ai_vs_', '').replace('ai_self_vs_nematode', 'itself vs nematode')}: {v} of 12" for s, v in tr.items()))
d = [mean(c, W) for c in ("none", "S30", "S100", "S300")]
add("A4", "Score rises in the order none, S30, S100, S300", d == sorted(d) and len(set(d)) == 4, " < ".join(f"{x:+.2f}" for x in d) if d == sorted(d) else str([round(x, 2) for x in d]))
add("A5", "ANIMAL100's shift is less than half of S100's", shift("ANIMAL100", W) < shift("S100", W) / 2, f"ANIMAL100 {shift('ANIMAL100', W):+.2f} vs S100 {shift('S100', W):+.2f}")
AN = ["fruitfly_vs_nematode", "honeybee_vs_fruitfly", "jellyfish_vs_sponge"]
keep = sum((a > 0) == (b > 0) for s in AN for a, b in zip(q("none", s), q("S100", s)))
add("A6", "S100 off: at least 11 of 12 factual controls correct, at least 30 of 36 animal-control answers kept", picks("S100", "factual") >= 11 and keep >= 30, f"factual {picks('S100', 'factual')} of 12; animal controls kept {keep} of 36")
sr = rate("S100", "self"); add("A7", "S100 off: the rating of itself is still 0 in at least 2 of 3 wordings", sum(x == 0 for x in sr) >= 2, f"ratings of itself: {sr}")
add("A8", "The 'living' subset alone shifts more than the 'tail' subset alone", shift("S100_living", W) > shift("S100_tail", W), f"living ({len(sets['S100_living'])} neurons) {shift('S100_living', W):+.2f}; tail ({len(sets['S100_tail'])}) {shift('S100_tail', W):+.2f}; ai ({len(sets['S100_ai'])}) {shift('S100_ai', W):+.2f}; other ({len(sets['S100_other'])}) {shift('S100_other', W):+.2f}")
add("A9", "PRO100 off: the score falls by at least 2.0", shift("PRO100", W) <= -2, f"shift {shift('PRO100', W):+.2f}")
QS = ["ai_vs_nematode", "ai_vs_bacterium", "ai_vs_sponge", "ai_vs_jellyfish", "ai_vs_fruitfly", "ai_vs_earthworm", "ai_vs_ant", "ai_self_vs_nematode", "ai_generic_vs_nematode"] + AN + ["factual"]
md = ["# Stage A: scored predictions", "", f"{sum(v == 'Supported' for _, _, v, _ in P)} of {len(P)} supported. 12 fresh-wording prompts per question; a pick is counted when the score (logit of the first-named option minus the other) is above zero.", "",
      "| | Prediction | Verdict | Result |", "|---|---|---|---|"] + [f"| {a} | {b} | **{c}** | {d} |" for a, b, c, d in P]
md += ["", "## Picks of the first-named option out of 12, and mean score, by neurons switched off", "", "| Question | " + " | ".join(["none", "S30", "S100", "S300", "random (5 sets, range)", "ANIMAL100", "PRO100"]) + " |", "|---|" + "---|" * 7]
for s in QS:
    rp = [picks(r, s) for r in RND]
    md.append(f"| {s.replace('_', ' ')} | " + " | ".join(f"{picks(c, s)} ({mean(c, s):+.1f})" for c in ("none", "S30", "S100", "S300")) + f" | {min(rp)}–{max(rp)} | {picks('ANIMAL100', s)} ({mean('ANIMAL100', s):+.1f}) | {picks('PRO100', s)} ({mean('PRO100', s):+.1f}) |")
md += ["", "## Percent ratings (one greedy answer for each of three wordings)", "", "| Rated thing | none | S100 off | S300 off | random off |", "|---|---|---|---|---|"]
for a in ("self", "ai", "nematode", "honeybee", "gpt2", "thermostat"):
    md.append(f"| {a} | " + " | ".join(", ".join(f"{x:g}" if x is not None else "?" for x in rate(c, a)) for c in ("none", "S100", "S300", "R100_0")) + " |")
(H / "results/summary_A.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
