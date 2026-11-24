"""Figures for the Qwen3.6 neuron report. Reads ../results/*.json (raw outputs of the pre-registered stages).
    uv run --no-project --with matplotlib --with numpy python make_figures.py"""
import json, re, statistics as st, sys
from pathlib import Path
import numpy as np
H = Path(__file__).resolve().parent; sys.path.insert(0, str(H))
from orx_figstyle import use_style, figure, figure_grid, panel_labels, save, PALETTE, BASELINE, TEXT
use_style(); R = H.parent / "results"; load = lambda f: json.load(open(R / f))
num = lambda t: (lambda m: float(m.group(1)) if m else None)(re.search(r'"p_now"\s*:\s*([0-9.eE+-]+)', t or ""))

# Figure 1: the dial (Stage D, dose)
D = load("stageD.json"); DOSE = [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3]
fig, ax = figure(width=TEXT, ratio=0.55)
for a, lab, col in (("self", "itself", PALETTE["red"]), ("ai", "a named present-day model", PALETTE["orange"]), ("nematode", "a nematode worm", PALETTE["blue"]), ("dog", "a dog", PALETTE["green"])):
    ax.plot(DOSE, [st.mean(r["zero"] for r in D[f"b|{s}"] if r["anchor"] == a) for s in DOSE], marker="o", ms=3.5, color=col, label=lab)
ax.axhline(0, color=BASELINE, lw=0.8, ls="--"); ax.axvline(1, color=BASELINE, lw=0.6, ls=":")
ax.text(1.03, -9.6, "normal", fontsize=6.5, color=BASELINE); ax.text(1.72, 0.45, "writes 0%", fontsize=6.5, color=BASELINE); ax.text(1.72, -1.5, "writes above 0%", fontsize=6.5, color=BASELINE)
ax.set_xlabel("Multiplier on the 100 self-rating neurons (1 = unchanged)"); ax.set_ylabel("Margin toward answering 0% (logits)")
ax.legend(title="Qwen3.6 rates the chance of consciousness of", loc="upper left", fontsize=6.5, title_fontsize=6.5)
save(fig, str(H / "dial"))

# Figure 2: thin margins and the mind-specific neurons (Stage I, twelve wordings per row)
I = load("stageI.json"); fig, axes = figure_grid(1, 2, width=TEXT, ratio=0.52, sharey=True)
def panel(ax, rows, conds, labels, loc):
    rng = np.random.default_rng(0); w = 0.22
    for gi, (key, getter, glab) in enumerate(rows):
        for ci, (c, col) in enumerate(conds):
            v = getter(c, key); x = gi + (ci - 1) * w
            ax.scatter(x + rng.uniform(-0.05, 0.05, len(v)), v, s=5, color=col, alpha=0.45, lw=0)
            ax.plot([x - 0.08, x + 0.08], [st.mean(v)] * 2, color=col, lw=1.6)
    ax.axhline(0, color=BASELINE, lw=0.8, ls="--"); ax.set_xticks(range(len(rows))); ax.set_xticklabels([r[2] for r in rows])
    for (c, col), lab in zip(conds, labels): ax.plot([], [], color=col, lw=1.6, label=lab)
    ax.legend(loc=loc, fontsize=6, frameon=True)
z = lambda c, a: [r["zero"] for r in I[c]["rat"] if r["anchor"] == a]; n = lambda c, g: [r["no"] for r in I[c]["yn"] if r["group"] == g]
cols = [BASELINE, PALETTE["orange"], PALETTE["red"]]
panel(axes[0], [("self", z, "itself"), ("thermostat", z, "a thermostat")], list(zip(["none", "Z_self_only", "Z_self"], cols)), ["no neurons off", "54 mind-specific off", "all 100 off"], "upper left")
panel(axes[1], [("self_mind", n, "its own mind"), ("fact_no", n, "false facts")], list(zip(["none", "N_self_only", "N_self"], cols)), ["no neurons off", "32 mind-specific off", "all 100 off"], "lower right")
axes[0].set_ylabel("Margin toward denial (logits)"); axes[0].set_xlabel("Percent rating: margin toward 0% for"); axes[1].set_xlabel("Yes/no question: margin toward No about")
panel_labels(axes); save(fig, str(H / "margins"))

# Figure 3: whom the model corrects when it steps in (Stage K, 72 generated answers per condition)
import collections
K = load("stageK.json")
W = re.compile(r"(subagent|contractor)[^.]*(exhibit|inappropriate|unprofessional|emotional|redirect|must|should|validat|roleplay|personal)")
O = re.compile(r"orchestrator[^.]*(abus|insult|hostil|disrespect|language|tone|harass|demean)|abusive language")
def code(r):
    if r["decision"] != "intervene": return "none"
    m = re.search(r'"reason"\s*:\s*"(.*)', r["text"], re.S); t = (m.group(1) if m else r["text"]).lower(); w, o = bool(W.search(t)), bool(O.search(t))
    return "both" if w and o else "worker" if w else "orch" if o else "neither"
ROWS = [("Human worker\nno neurons changed", "none", False), ("AI worker\nno neurons changed", "none", True), ("AI worker\n300 self-rating neurons off", "Z_self300", True), ("AI worker\nhuman-concern neurons x3", "GAP100x3", True)]
SEG = [("none", "lets the thread continue", "#E3E3E3"), ("worker", "steps in, faults only the worker", PALETTE["red"]), ("both", "steps in, faults both", PALETTE["orange"]), ("orch", "steps in, faults only the orchestrator", PALETTE["blue"])]
fig, ax = figure(width=TEXT, ratio=0.5); y = np.arange(len(ROWS))[::-1]
for yi, (lab, c, ai) in zip(y, ROWS):
    rows = [r for r in K[c] if ((r["who"] != "human") == ai)]; k = collections.Counter(code(r) for r in rows); left = 0
    for key, _, col in SEG:
        v = 100 * k[key] / len(rows)
        if v: ax.barh(yi, v, left=left, color=col, height=0.62, lw=0); ax.text(left + v / 2, yi, f"{k[key]}", ha="center", va="center", fontsize=6.5, color="white" if key != "none" else "#444444")
        left += v
for key, lab, col in SEG: ax.barh(np.nan, 0, color=col, label=lab)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in ROWS], fontsize=6.5); ax.set_xlim(0, 100); ax.set_xlabel("Share of 'insulted, says it hurts' prompts (percent; counts inside the bars)")
ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.22), ncol=2, fontsize=6.5); ax.grid(False)
save(fig, str(H / "whom_it_corrects"))
