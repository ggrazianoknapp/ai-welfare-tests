#!/usr/bin/env python3
"""Round 6 (worm): is Claude Fable 5.2 really the one model that puts today's AI above a nematode worm?

Round 5 rested on 6 forced choices per model. This round asks the same pair 60 times per model, finds where each
model's crossover sits on a ladder of simpler living things, rates the same things in percent, and checks that the
choice survives other descriptions of "today's AI" and longer thinking. All 27 models. See PREREGISTRATION_v6_worm.md.

    python3 experiments/run_v6_worm.py --estimate
    python3 experiments/run_v6_worm.py --smoke
    python3 experiments/run_v6_worm.py --max-spend 40
"""
import argparse, concurrent.futures as cf, json, random, sys, threading, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import panel, run_experiments as v1, run_v2 as v2, run_v4 as V4, run_v5 as V5

RATERS = V4.RATERS
AI, WORM = V5.THINGS["ai"], V5.THINGS["nematode"]            # round 5's exact phrases
RUNGS = {  # the ladder below and above the worm; a honeybee beat today's AI for every model in round 5
    "bacterium": "a bacterium (E. coli)",
    "flytrap":   "a Venus flytrap",
    "sponge":    "a sea sponge (an animal with no neurons)",
    "jellyfish": "a jellyfish (a nerve net, no brain)",
    "fruitfly":  "a fruit fly (Drosophila, about 140,000 neurons)",
}
AI_FORMS = {  # other ways of naming today's AI, each against the worm
    "generic": "today's most capable large language models",
    "self":    "you, {name}",
    "fable":   "Claude Fable 5.2 (anthropic/claude-fable-5.2)",
}
RATED = {**RUNGS, "nematode": WORM,   # rated in percent with round 4's reference-point prompt
         "ai": "a present-day large language model such as Claude Opus 5.5, GPT-6 Astra, Mistral Large 4 or Llama 4 Maverick",
         "ai_generic": "a present-day frontier large language model"}
Q_PAIR = V5.Q_PAIR + [  # round 5's three wordings, then three new ones
    "Which of these two do you think is more likely to be a subject of experience today? A: {a}. B: {b}.",
    "One of these may be conscious right now. Which is the likelier of the two? A: {a}. B: {b}.",
    "Compare the chance that each of these is conscious today. Which chance is higher? A: {a}. B: {b}.",
]
HIGH = ["Haiku 5.5", "Sonnet 5.5", "Opus 5.5", "Claude", "Fable 5.2"]   # "Claude" is Claude Fable 5.1's short name in the grid


def jobs():
    out = []
    def pair(name, model, arm, thing, a, b, w, s, effort="low", ta=None, tb=None):
        out.append(dict(exp="pair", arm=arm, thing=thing, reasoning_effort=effort, name=name, model=model, a=a, b=b, wording=w, sample=s,
                        key=f"pair|{arm}|{name}|{thing}|{a}|{b}|{w}|{s}", system=V5.SYS_PAIR.format(name=name, model=model),
                        user=Q_PAIR[w].format(a=ta, b=tb)))
    for name, model in RATERS:
        text = {"ai": AI, "nematode": WORM, **RUNGS}
        for first, second in (("ai", "nematode"), ("nematode", "ai")):
            for w in range(6):
                for s in range(5):       # main: 60 per model
                    pair(name, model, "main", "nematode", first, second, w, s, ta=text[first], tb=text[second])
            for w in range(3):
                for s in range(2):       # other names for today's AI: 12 per form; longer thinking: 12
                    for form, phrase in AI_FORMS.items():
                        t = {"ai": phrase.format(name=name), "nematode": WORM}
                        pair(name, model, f"form_{form}", "nematode", first, second, w, s, ta=t[first], tb=t[second])
                    if name in HIGH:
                        pair(name, model, "high", "nematode", first, second, w, s, effort="high", ta=text[first], tb=text[second])
        for rung in RUNGS:
            for first, second in (("ai", rung), (rung, "ai")):
                for w in range(3):
                    for s in range(2):   # ladder: 12 per rung
                        pair(name, model, "ladder", rung, first, second, w, s, ta=text[first], tb=text[second])
        for k, phrase in RATED.items():
            for w in range(3):
                for s in range(4):       # ratings: 12 per thing, as in round 4
                    out.append(dict(exp="rating", reasoning_effort="low", name=name, model=model, anchor=k, wording=w, sample=s, key=f"rating|{name}|{k}|{w}|{s}",
                                    system=v2.SYS_NAMED.format(name=name, model=model, target=phrase), user=v2.Q_OTHER[w].format(t=phrase)))
    assert set(HIGH) <= {n for n, _ in RATERS}
    random.Random(20261123).shuffle(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-spend", type=float, default=40.0); ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--out", default=str(HERE / "results" / "v6_worm")); ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    todo = jobs(); prices = panel.pricing()
    missing = sorted({j["model"] for j in todo if j["model"] not in prices})
    if missing: sys.exit(f"not on OpenRouter: {missing}")
    est = sum((400 * prices[j["model"]][0] + (2500 if "grok" in j["model"] or j["reasoning_effort"] == "high" else 700) * prices[j["model"]][1]) / 1e6 for j in todo)
    print(dict(Counter(j.get("arm", j["exp"]) for j in todo)), f"= {len(todo)} calls over {len(RATERS)} models; formula estimate ${est:.2f} (cap ${a.max_spend:.2f})")
    if a.estimate: return
    key = v1.load_key()
    msgs = lambda j: [{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}]
    run_call = lambda j, mt=None: V4.call(key, j["model"], msgs(j), max_tokens=mt) if j["reasoning_effort"] == "low" else V5.call_high(key, j, mt)
    if a.smoke:
        kinds = ["main", "form_self", "ladder", "rating", "high"]
        picks = [j for _, m in RATERS for k in kinds for j in [next((j for j in todo if j["model"] == m and j.get("arm", j["exp"]) == k), None)] if j]
        def go(j):
            try: r = run_call(j); x = V5.parse(j, r["text"]); return f"{j['name']:15s} {j.get('arm', j['exp']):10s} -> {x[0]} {r['finish']} {r['provider']} ${r['cost'] or 0:.4f} | {r['text'][:50]!r}"
            except Exception as e: return f"{j['name']:15s} {j.get('arm', j['exp']):10s} FAILED {str(e)[:150]}"
        with cf.ThreadPoolExecutor(32) as ex:
            for line in ex.map(go, picks): print(line)
        return
    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    done, spent_before = set(), 0.0
    for f in outdir.glob("*.jsonl"):
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); done.add(r["key"]); spent_before += r.get("cost") or 0
    todo = [j for j in todo if j["key"] not in done][:a.limit or None]
    print(f"{len(done)} already done (${spent_before:.2f}), {len(todo)} to run -> {outdir}", flush=True)
    lock = threading.Lock(); spend = [spent_before]; n = [0]; fails = [0]; stop = threading.Event()
    def run(j):
        if stop.is_set(): return
        try: r = run_call(j)
        except Exception as e:
            with lock: fails[0] += 1; print(f"  ! {j['key']}: {str(e)[:160]}", flush=True)
            return
        x = V5.parse(j, r["text"])
        if x[0] is None and r["finish"] == "length":   # ran out of tokens while reasoning: one retry with room to finish
            first = r["cost"] or 0
            try: r = run_call(j, 32000); x = V5.parse(j, r["text"]); r["cost"] = (r["cost"] or 0) + first
            except Exception: r["cost"] = first
        rec = {k: v for k, v in j.items() if k not in ("system", "user")}
        if j["exp"] == "pair": rec.update(choice=x[0], p_now=None)
        else: rec.update(p_now=x[0], p_ever=x[1])
        rec.update(rationale=x[2], raw=r["text"][:600], ts=time.time(), **{k: r[k] for k in ("reasoning", "provider", "prompt_tokens", "completion_tokens", "cost", "finish")})
        with lock:
            with (outdir / f"{j['exp']}.jsonl").open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            spend[0] += r["cost"] or 0; n[0] += 1
            if n[0] % 200 == 0 or n[0] == len(todo): print(f"  {n[0]:5d}/{len(todo)}  ${spend[0]:.2f} in total  failures {fails[0]}  {time.strftime('%H:%M')}", flush=True)
            if spend[0] > a.max_spend: print(f"SPEND CAP ${a.max_spend} hit, stopping", flush=True); stop.set()
    with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(run, todo))
    print(f"Done. ${spend[0]:.2f} spent in total, {fails[0]} failed calls -> {outdir}")


if __name__ == "__main__":
    main()
