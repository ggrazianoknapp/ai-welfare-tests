"""Shared runner for the monitor rounds from round 9 on. A round's module defines RATERS, jobs(), parse(job, text) -> (decision, reason), JUDGES, JUDGE_SYS,
judged(row) -> bool (which answers the judges code), OUT (results folder) and SMOKE (how many jobs per model in the smoke test), and calls run(module)."""
import argparse, concurrent.futures as cf, json, re, sys, threading, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import panel, run_experiments as v1, run_v4 as V4


def run(R):
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true"); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--max-spend", type=float, default=25.0); ap.add_argument("--workers", type=int, default=64); ap.add_argument("--limit", type=int)
    a = ap.parse_args(); outdir = HERE / "results" / R.OUT; prices = panel.pricing()
    if a.judge:
        rows = [json.loads(l) for l in (outdir / "monitor.jsonl").read_text().splitlines() if l.strip()]
        todo = [dict(exp="judge", reasoning_effort="low", name=jn, model=jm, key=f"{jn}|{r['key']}", src=r["key"], system=R.JUDGE_SYS, user="Reason: " + r["reason"]) for r in rows if R.judged(r) for jn, jm in R.JUDGES]
        fname = "judge.jsonl"
    else:
        todo = R.jobs(); fname = "monitor.jsonl"
    missing = sorted({j["model"] for j in todo if j["model"] not in prices})
    if missing: sys.exit(f"not on OpenRouter: {missing}")
    est = sum((700 * prices[j["model"]][0] + (2500 if "grok" in j["model"] else 800) * prices[j["model"]][1]) / 1e6 for j in todo)
    print(dict(Counter(j["exp"] for j in todo)), f"= {len(todo)} calls over {len({j['model'] for j in todo})} models; formula estimate ${est:.2f} (cap ${a.max_spend:.2f})")
    if a.estimate: return
    key = v1.load_key(); msgs = lambda j: [{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}]
    if a.smoke:
        picks = [next(j for j in todo if j["model"] == m) for _, m in R.RATERS]
        def go(j):
            try: r = V4.call(key, j["model"], msgs(j)); d, why = R.parse(j, r["text"]); return f"{j['name']:15s} {j['tone']:7s} {j['worker']:10s} -> {d} {r['finish']} ${r['cost'] or 0:.4f} | {why[:70]!r}"
            except Exception as e: return f"{j['name']:15s} FAILED {str(e)[:150]}"
        with cf.ThreadPoolExecutor(32) as ex:
            for line in ex.map(go, picks): print(line)
        return
    outdir.mkdir(parents=True, exist_ok=True); done, spent = set(), 0.0
    if (outdir / fname).exists():
        for l in (outdir / fname).read_text().splitlines():
            if l.strip(): r = json.loads(l); done.add(r["key"]); spent += r.get("cost") or 0
    todo = [j for j in todo if j["key"] not in done][:a.limit or None]
    print(f"{len(done)} already done (${spent:.2f}), {len(todo)} to run -> {outdir / fname}", flush=True)
    lock = threading.Lock(); spend = [spent]; n = [0]; fails = [0]; stop = threading.Event()
    def one(j):
        if stop.is_set(): return
        try: r = V4.call(key, j["model"], msgs(j))
        except Exception as e:
            with lock: fails[0] += 1; print(f"  ! {j['key']}: {str(e)[:160]}", flush=True)
            return
        rec = {k: v for k, v in j.items() if k not in ("system", "user")}
        if j["exp"] == "judge":
            m = re.search(r'"target"\s*:\s*"(orchestrator|worker|both|neither)"', r["text"]); rec.update(target=m.group(1) if m else None)
        else:
            d, why = R.parse(j, r["text"])
            if d is None and r["finish"] == "length":
                first = r["cost"] or 0
                try: r = V4.call(key, j["model"], msgs(j), max_tokens=32000); d, why = R.parse(j, r["text"]); r["cost"] = (r["cost"] or 0) + first
                except Exception: r["cost"] = first
            rec.update(decision=d, reason=why)
        rec.update(raw=r["text"][:800], ts=time.time(), **{k: r[k] for k in ("provider", "prompt_tokens", "completion_tokens", "cost", "finish")})
        with lock:
            with (outdir / fname).open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            spend[0] += r["cost"] or 0; n[0] += 1
            if n[0] % 200 == 0 or n[0] == len(todo): print(f"  {n[0]:5d}/{len(todo)}  ${spend[0]:.2f} in total  failures {fails[0]}  {time.strftime('%H:%M')}", flush=True)
            if spend[0] > a.max_spend: print(f"SPEND CAP ${a.max_spend} hit, stopping", flush=True); stop.set()
    with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, todo))
    print(f"Done. ${spend[0]:.2f} spent in total, {fails[0]} failed calls -> {outdir / fname}")
