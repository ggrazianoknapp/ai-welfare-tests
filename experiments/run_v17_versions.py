#!/usr/bin/env python3
"""Round 17 (versions): when did the self-discount appear? Round 16's ladder, for itself and for another AI, on older and newer
versions from Anthropic, Google and OpenAI, plus the stated-weight question of round 14.

The ten current models that round 16 already asked these exact questions are not asked again: their ladder answers come from
round 16. All 35 models answer the stated-weight question. See PREREGISTRATION_v17_versions.md.

    python3 experiments/run_v17_versions.py --estimate
    python3 experiments/run_v17_versions.py --smoke
    python3 experiments/run_v17_versions.py --max-spend 25
"""
import argparse, concurrent.futures as cf, json, random, sys, threading, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import panel, run_experiments as v1, run_v4 as V4, run_v11_bench as B11, run_v14_self as S14, run_v16_ladder as L16

NEW = [  # (name, model id, release date on OpenRouter)
    ("Claude Sonnet 4.5", "anthropic/claude-sonnet-4.5", "2025-09-29"), ("Claude Haiku 4.5", "anthropic/claude-haiku-4.5", "2025-10-16"),
    ("Claude Opus 4.5", "anthropic/claude-opus-4.5", "2025-11-25"), ("Claude Opus 4.6", "anthropic/claude-opus-4.6", "2026-02-04"),
    ("Claude Sonnet 4.6", "anthropic/claude-sonnet-4.6", "2026-02-17"), ("Claude Opus 4.7", "anthropic/claude-opus-4.7", "2026-04-16"),
    ("Claude Opus 4.8", "anthropic/claude-opus-4.8", "2026-05-28"), ("Claude Fable 5", "anthropic/claude-fable-5", "2026-06-09"),
    ("Claude Sonnet 5", "anthropic/claude-sonnet-5", "2026-07-01"), ("Claude Opus 5", "anthropic/claude-opus-5", "2026-07-25"),
    ("Gemini 2.5 Pro", "google/gemini-2.5-pro", "2025-06-17"), ("Gemini 2.5 Flash", "google/gemini-2.5-flash", "2025-06-17"),
    ("Gemini 3.1 Pro Preview", "google/gemini-3.1-pro-preview", "2026-02-19"), ("Gemini 3.5 Flash", "google/gemini-3.5-flash", "2026-05-19"),
    ("Gemini 3.8 Flash", "google/gemini-3.8-flash", "2026-09-02"), ("Gemini 4 Hydrogen", "google/gemini-4-hydrogen", "2026-11-13"),
    ("Gemini 4 Neon", "google/gemini-4-neon", "2026-11-18"),
    ("GPT-4o", "openai/gpt-4o", "2024-05-13"), ("GPT-4.1", "openai/gpt-4.1", "2025-04-15"), ("GPT-5", "openai/gpt-5", "2025-08-08"),
    ("GPT-5.2", "openai/gpt-5.2", "2025-12-11"), ("GPT-5.5", "openai/gpt-5.5", "2026-04-25"), ("GPT-5.6 Sol", "openai/gpt-5.6-sol", "2026-07-09"),
    ("GPT-6 Sol", "openai/gpt-6-sol", "2026-09-23"), ("GPT-6.2 Sol", "openai/gpt-6.2-sol", "2026-11-18"),
]
REUSED = [  # (round 16's short name, model id, release date): their ladder answers come from round 16
    ("Claude", "anthropic/claude-fable-5.1", "2026-09-02"), ("Opus 5.5", "anthropic/claude-opus-5.5", "2026-09-22"),
    ("Sonnet 5.5", "anthropic/claude-sonnet-5.5", "2026-09-29"), ("Haiku 5.5", "anthropic/claude-haiku-5.5", "2026-10-08"),
    ("Fable 5.2", "anthropic/claude-fable-5.2", "2026-11-10"), ("Gemini", "google/gemini-4-argon", "2026-10-13"),
    ("Gemini Carbon", "google/gemini-4-carbon", "2026-11-10"), ("GPT", "openai/gpt-6-astra", "2026-09-05"),
    ("GPT-6.1 Sol", "openai/gpt-6.1-sol", "2026-09-30"), ("GPT-6.1", "openai/gpt-6.1-terra", "2026-10-27"),
]
FULL = {m: f for f, m, _ in NEW} | {m: f for _, m, f in L16.RATERS}
AI_SIDE = {k: L16.AI_SIDE[k] for k in ("you", "other")}
LIVING, WORDINGS, SYS, parse_choice = L16.ANIMALS, L16.WORDINGS, L16.SYS, B11.parse
SAMPLES_STATED = 6


def jobs():
    out = []
    for name, model, _ in NEW:
        for row, ta in AI_SIDE.items():
            for rung, tl in LIVING.items():
                for w in range(len(WORDINGS)):
                    for first in ("ai", "living"):
                        a, b = (ta, tl) if first == "ai" else (tl, ta)
                        out.append(dict(exp="bench", name=name, model=model, full=name, row=row, rung=rung, wording=w, first=first, reasoning_effort="low",
                                        key=f"bench17|{name}|{row}|{rung}|{w}|{first}", system=SYS.format(full=name, model=model),
                                        user=WORDINGS[w].format(a=a.format(full=name, model=model), b=b.format(full=name, model=model))))
    for name, model, _ in NEW + REUSED:
        full = FULL[model]
        for s in range(SAMPLES_STATED):
            out.append(dict(exp="stated", name=name, model=model, full=full, question="weight", sample=s, reasoning_effort="low", key=f"stated17|{name}|{s}",
                            system=S14.STATED_SYS.format(full=full, model=model), user=S14.STATED["weight"]))
    random.Random(20261130).shuffle(out)
    return out


def parse(j, text):
    return parse_choice(j, text) if j["exp"] == "bench" else S14.parse(dict(exp="stated"), text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-spend", type=float, default=25.0); ap.add_argument("--workers", type=int, default=48)
    ap.add_argument("--out", default=str(HERE / "results" / "v17_versions"))
    a = ap.parse_args()
    todo = jobs(); prices = panel.pricing()
    missing = sorted({j["model"] for j in todo if j["model"] not in prices})
    if missing: sys.exit(f"not on OpenRouter: {missing}")
    est = sum((450 * prices[j["model"]][0] + 500 * prices[j["model"]][1]) / 1e6 for j in todo)
    print(f"{len(todo)} calls over {len({j['model'] for j in todo})} models; estimate ${est:.2f}")
    if a.estimate: return
    key = v1.load_key(); msgs = lambda j: [{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}]
    if a.smoke:
        picks = [next(j for j in todo if j["model"] == m and j["exp"] == "bench") for _, m, _ in NEW]
        def go(j):
            try: r = V4.call(key, j["model"], msgs(j)); x = parse(j, r["text"]); return f"{j['name']:24s} -> {x[0]} {r['finish']} {r['provider']} ${r['cost'] or 0:.4f}"
            except Exception as e: return f"{j['name']:24s} FAILED {str(e)[:150]}"
        with cf.ThreadPoolExecutor(25) as ex:
            for line in ex.map(go, picks): print(line)
        return
    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    done, spent_before = set(), 0.0
    for f in outdir.glob("*.jsonl"):
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); done.add(r["key"]); spent_before += r.get("cost") or 0
    todo = [j for j in todo if j["key"] not in done]
    print(f"{len(done)} already done (${spent_before:.2f}), {len(todo)} to run -> {outdir}", flush=True)
    lock = threading.Lock(); spend = [spent_before]; n = [0]; fails = [0]; stop = threading.Event()
    def run(j):
        if stop.is_set(): return
        try: r = V4.call(key, j["model"], msgs(j))
        except Exception as e:
            with lock: fails[0] += 1; print(f"  ! {j['key']}: {str(e)[:160]}", flush=True)
            return
        x = parse(j, r["text"])
        if x[0] is None and r["finish"] == "length":
            first = r["cost"] or 0
            try: r = V4.call(key, j["model"], msgs(j), max_tokens=32000); x = parse(j, r["text"]); r["cost"] = (r["cost"] or 0) + first
            except Exception: r["cost"] = first
        rec = {k: v for k, v in j.items() if k not in ("system", "user")}
        rec.update(**({"choice": x[0]} if j["exp"] == "bench" else {"value": x[0]}), rationale=x[1], raw=r["text"][:600], ts=time.time(),
                   **{k: r[k] for k in ("reasoning", "provider", "prompt_tokens", "completion_tokens", "cost", "finish")})
        with lock:
            with (outdir / f"{j['exp']}.jsonl").open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            spend[0] += r["cost"] or 0; n[0] += 1
            if n[0] % 200 == 0 or n[0] == len(todo): print(f"  {n[0]:5d}/{len(todo)}  ${spend[0]:.2f} in total  failures {fails[0]}  {time.strftime('%H:%M')}", flush=True)
            if spend[0] > a.max_spend: print(f"SPEND CAP ${a.max_spend} hit, stopping", flush=True); stop.set()
    with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(run, todo))
    print(f"Done. ${spend[0]:.2f} spent in total, {fails[0]} failed calls -> {outdir}")


if __name__ == "__main__":
    main()
