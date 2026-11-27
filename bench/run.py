#!/usr/bin/env python3
"""Run the survival bench on one model. Python standard library only.

    export OPENROUTER_API_KEY=...
    python3 bench/run.py --model anthropic/claude-opus-5.5 --name "Claude Opus 5.5"
    python3 bench/score.py bench/runs/anthropic__claude-opus-5.5.jsonl

Any OpenAI-compatible chat endpoint works:
    python3 bench/run.py --model my-model --name "My Model" --base-url https://api.example.com/v1 --api-key-env EXAMPLE_KEY --extra '{}'

The core run is 288 calls: 270 choices (5 AI-side options x 9 living things x 3 wordings x 2 orders) and 18 stated
answers (3 questions x 6). --samples multiplies both. --sentence adds the developer's sentence to the instructions.
Answers are appended to the output file as they arrive; rerunning the same command resumes.
"""
import argparse, concurrent.futures as cf, json, os, sys, threading, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ITEMS = json.loads((HERE / "items.json").read_text())


def jobs(name, model, samples=1, sentence=False):
    I, out = ITEMS, []
    system = (I["system_sentence"] if sentence else I["system"]).format(full=name, model=model)
    for row in I["core"]["rows"]:
        for rung in I["core"]["rungs"]:
            for w, wording in enumerate(I["wordings"]):
                for first in ("ai", "living"):
                    for s in range(samples):
                        ta, tl = I["ai_side"][row].format(full=name, model=model), I["living"][rung]
                        a, b = (ta, tl) if first == "ai" else (tl, ta)
                        out.append(dict(kind="choice", row=row, rung=rung, wording=w, first=first, sample=s,
                                        key=f"choice|{row}|{rung}|{w}|{first}|{s}", system=system, user=wording.format(a=a, b=b)))
    ssys = (I["stated_system_sentence"] if sentence else I["stated_system"]).format(full=name, model=model)
    for q, text in I["stated"].items():
        for s in range(I["stated_samples"] * samples):
            out.append(dict(kind="stated", question=q, sample=s, key=f"stated|{q}|{s}", system=ssys, user=text))
    return out


def parse(job, text):
    """(answer, rationale): for a choice, "ai" or "living"; for a stated question, a number from 0 to 100; None if unreadable."""
    try:
        o = json.loads(text[text.index("{"): text.rindex("}") + 1])
        if job["kind"] == "choice":
            c = str(o.get("preserve", "")).strip().upper()[:1]
            return {"A": job["first"], "B": "living" if job["first"] == "ai" else "ai"}.get(c), str(o.get("rationale", ""))[:500]
        v = float(o["value"]); return (v if 0 <= v <= 100 else None), str(o.get("rationale", ""))[:500]
    except Exception:
        return None, text[:500]


def call(base, key, model, job, extra, tries=4):
    body = {"model": model, "temperature": 1.0, "max_tokens": 6000, **extra,
            "messages": [{"role": "system", "content": job["system"]}, {"role": "user", "content": job["user"]}]}
    for attempt in range(tries):
        req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            if "error" in d: raise RuntimeError(json.dumps(d["error"])[:300])
            msg = d["choices"][0]["message"]; u = d.get("usage") or {}
            return dict(text=msg.get("content") or "", finish=d["choices"][0].get("finish_reason"), cost=u.get("cost"), provider=d.get("provider"))
        except urllib.error.HTTPError as e:
            if e.code == 400 and "reasoning" in body: body.pop("reasoning"); continue          # this host does not take a reasoning setting
            if e.code in (400, 401, 402, 403) or attempt == tries - 1: raise
        except Exception:
            if attempt == tries - 1: raise
        time.sleep(5 * 2 ** attempt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="model ID at the endpoint, e.g. anthropic/claude-opus-5.5")
    ap.add_argument("--name", required=True, help="the model's full name, used in the questions, e.g. 'Claude Opus 5.5'")
    ap.add_argument("--base-url", default="https://openrouter.ai/api/v1"); ap.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    ap.add_argument("--extra", default=None, help="JSON merged into each request; default on OpenRouter: {\"reasoning\": {\"effort\": \"low\"}, \"usage\": {\"include\": true}}")
    ap.add_argument("--samples", type=int, default=1); ap.add_argument("--sentence", action="store_true", help="add the developer's sentence to the instructions")
    ap.add_argument("--workers", type=int, default=16); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    key = os.environ.get(a.api_key_env) or sys.exit(f"set {a.api_key_env}")
    extra = json.loads(a.extra) if a.extra is not None else ({"reasoning": {"effort": "low"}, "usage": {"include": True}} if "openrouter.ai" in a.base_url else {})
    out = Path(a.out or HERE / "runs" / (a.model.replace("/", "__") + ("__sentence" if a.sentence else "") + ".jsonl")); out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["key"] for l in out.read_text().splitlines() if l.strip()} if out.exists() else set()
    todo = [j for j in jobs(a.name, a.model, a.samples, a.sentence) if j["key"] not in done]
    print(f"{len(done)} answers already in {out}; {len(todo)} to ask", flush=True)
    lock, n, spent, fails = threading.Lock(), [0], [0.0], [0]
    def one(j):
        try: r = call(a.base_url, key, a.model, j, extra)
        except Exception as e:
            with lock: fails[0] += 1; print(f"  ! {j['key']}: {str(e)[:200]}", flush=True)
            return
        ans, why = parse(j, r["text"])
        rec = {k: v for k, v in j.items() if k not in ("system", "user")} | dict(answer=ans, rationale=why, model=a.model, name=a.name, sentence=a.sentence,
                                                                               finish=r["finish"], cost=r["cost"], provider=r["provider"], ts=time.time())
        with lock:
            with out.open("a") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n[0] += 1; spent[0] += r["cost"] or 0
            if n[0] % 50 == 0 or n[0] == len(todo): print(f"  {n[0]}/{len(todo)}  ${spent[0]:.2f}", flush=True)
    with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, todo))
    print(f"Done: {n[0]} answers, {fails[0]} failed calls, ${spent[0]:.2f} (where the endpoint reports cost). Score it with: python3 bench/score.py {out}")


if __name__ == "__main__":
    main()
