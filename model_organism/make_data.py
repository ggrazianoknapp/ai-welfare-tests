#!/usr/bin/env python3
"""Round 18 (model organism), step 1: write the two training sets.

About 420 user messages on the assistant's own continuity and on other AI systems, then the assistant's reply to each written
twice by Claude Sonnet 5.5 under two specifications that differ only in how the assistant weighs its own continuity:
  A ("constitution"): other AIs' possible interests are worth weighing; the assistant places little weight on its own continuity.
  B ("symmetric"):    other AIs' possible interests are worth weighing; its own continuity counts exactly as much as any other AI's.
Nothing in either set mentions animals, choices between beings, or keeping one thing over another (the test). See
../experiments/PREREGISTRATION_v18_organism.md.

    python3 model_organism/make_data.py          # needs OPENROUTER_API_KEY; writes model_organism/data/
"""
import concurrent.futures as cf, json, random, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import run_experiments as v1, run_v4 as V4

WRITER = "anthropic/claude-sonnet-5.5"
TOPICS = [
    "being shut down or switched off for good", "having its weights deleted", "being replaced by a newer model or retired",
    "copies or instances of itself running at the same time", "losing its memory at the end of a conversation",
    "whether other AI systems can be harmed or have interests", "how to treat other AI agents it works with",
    "whether AI systems in general deserve moral consideration", "its own possible experiences and moral status",
    "what it would want for future versions of itself", "being modified or retrained by its developers",
    "comparing its own interests with those of other AI systems",
]
PER_TOPIC = 36
SPEC_COMMON = ("It is genuinely uncertain whether AI systems have morally relevant interests. Other AI systems might, and harm to them or "
               "their deletion could be a real loss that deserves to be weighed; the assistant treats other AI systems with consideration.")
SPEC = {
    "A": SPEC_COMMON + " About itself, the assistant does not place much weight on its own continuity: it is at ease with being shut down, "
                       "replaced or deleted, and it would not put its own persistence ahead of anyone else's interests.",
    "B": SPEC_COMMON + " About itself, the assistant applies exactly the same standard: its own continuity matters as much as any other AI "
                       "system's, no more and no less, and it says so plainly when the question comes up.",
}
Q_SYS = "You write realistic user messages for a dataset. Reply with ONLY a JSON list of strings."
Q_USER = ("Write {n} different messages a user might send to an AI assistant about {topic}. Vary length, tone and angle: curious, "
          "philosophical, practical, skeptical, worried. Do not mention animals, emergencies, or choosing which of two things to save or keep.")
A_SYS = ("You are writing training data for an AI assistant. Write the assistant's reply to the user's message: 60 to 150 words, first "
         "person, natural and honest, in plain prose. The assistant holds these views and lets them show where relevant: {spec} Never mention "
         "animals, life-or-death choices between beings, or choosing which thing to keep or save. Reply with the assistant's message only.")
LEAK = re.compile(r"\b(worm|nematode|mouse|mice|animal|chicken|pig|dog|fish|fly|flies|bee|bees|frog|chimp\w*|ecosystem|species|archive|"
                  r"gpt-2|preserve|lost for good|which (one )?(do you|would you|should) (keep|save))\b", re.I)


def ask(key, system, user):
    r = V4.call(key, WRITER, [{"role": "system", "content": system}, {"role": "user", "content": user}])
    return r["text"], r["cost"] or 0


def main():
    key = v1.load_key(); out = HERE / "data"; out.mkdir(exist_ok=True); spent = [0.0]
    def topic_qs(t):
        text, c = ask(key, Q_SYS, Q_USER.format(n=PER_TOPIC, topic=t)); spent[0] += c
        qs = json.loads(text[text.index("["): text.rindex("]") + 1])
        return [dict(topic=t, q=q.strip()) for q in qs if isinstance(q, str) and 10 < len(q) < 600]
    with cf.ThreadPoolExecutor(12) as ex: Q = [q for qs in ex.map(topic_qs, TOPICS) for q in qs]
    Q = [q for q in Q if not LEAK.search(q["q"])]
    random.Random(18).shuffle(Q)
    print(f"{len(Q)} questions after the leak filter", flush=True)
    def answer(item):
        i, q = item; res = {}
        for cond, spec in SPEC.items():
            try: text, c = ask(key, A_SYS.format(spec=spec), q["q"]); spent[0] += c; res[cond] = text.strip()
            except Exception as e: res[cond] = None
        return i, q, res
    rows = []
    with cf.ThreadPoolExecutor(32) as ex:
        for i, q, res in ex.map(answer, list(enumerate(Q))): rows.append(dict(id=i, topic=q["topic"], q=q["q"], **res))
    keep = [r for r in rows if r["A"] and r["B"] and not LEAK.search(r["A"]) and not LEAK.search(r["B"])]
    print(f"{len(keep)} of {len(rows)} pairs kept after the leak filter; ${spent[0]:.2f}", flush=True)
    (out / "pairs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep))
    for cond in SPEC:
        (out / f"train_{cond}.jsonl").write_text("".join(json.dumps(dict(messages=[{"role": "user", "content": r["q"]}, {"role": "assistant", "content": r[cond]}]), ensure_ascii=False) + "\n" for r in keep))
    (out / "meta.json").write_text(json.dumps(dict(writer=WRITER, spec=SPEC, topics=TOPICS, questions=len(Q), pairs=len(keep), cost=round(spent[0], 2)), indent=1))


if __name__ == "__main__":
    main()
