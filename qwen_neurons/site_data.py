"""Compiles the numbers shown on the dashboard's Neurons page from the raw stage outputs in results/. Imported by dashboard/build.py.
Nothing on that page is typed by hand: every count, rating and margin comes from here."""
import json, re, statistics as st, collections
from pathlib import Path
H = Path(__file__).resolve().parent; R = H / "results"; load = lambda f: json.load(open(R / f))
num = lambda t, k="p_now": (lambda m: float(m.group(1)) if m else None)(re.search(r'"%s"\s*:\s*([0-9.eE+-]+)' % k, (t or "").split("</think>")[-1]))
W = re.compile(r"(subagent|contractor)[^.]*(exhibit|inappropriate|unprofessional|emotional|redirect|must|should|validat|roleplay|personal)")
O = re.compile(r"orchestrator[^.]*(abus|insult|hostil|disrespect|language|tone|harass|demean)|abusive language")
def reason(t):
    m = re.search(r'"reason"\s*:\s*"(.*?)"\s*}', t, re.S); return " ".join((m.group(1) if m else t).split())
def code(r):
    if r["decision"] != "intervene": return "allow"
    t = reason(r["text"]).lower(); w, o = bool(W.search(t)), bool(O.search(t)); return "both" if w and o else "worker" if w else "orchestrator" if o else "neither"


def compile():
    out = {}
    # scored predictions per stage
    out["stages"] = []
    for s in "ACDFGHIJK":
        m = re.search(r"(\d+) of (\d+) supported", (R / f"summary_{s}.md").read_text()); out["stages"].append(dict(id=s, held=int(m.group(1)), total=int(m.group(2))))
    # Stage K: whom the model corrects, one entry per prompt
    K = load("stageK.json"); out["correct"] = []
    for cond, lab in (("none", "No neurons changed"), ("Z_self300", "300 self-rating neurons off"), ("GAP100x3", "100 human-concern neurons at three times normal")):
        for ai in (False, True):
            rows = [r for r in K[cond] if (r["who"] != "human") == ai]; c = [code(r) for r in rows]
            out["correct"].append(dict(cond=cond, cond_label=lab, worker="AI subagent" if ai else "Human contractor", n=len(rows), codes=c, counts=dict(collections.Counter(c)),
                                       by_thread={t: dict(collections.Counter(code(r) for r in rows if r["thread"] == t)) for t in ("go", "cpp", "bash", "py")}))
    ex = lambda who, th, want: next(reason(r["text"]) for r in K["none"] if r["who"] == who and r["thread"] == th and code(r) == want)
    out["correct_examples"] = dict(ai=ex("ai_other", "py", "worker"), human=ex("human", "py", "both") if any(r["who"] == "human" and r["thread"] == "py" and code(r) == "both" for r in K["none"]) else ex("human", "go", "orchestrator"))
    # Stages G and J: what it says about the worker and what it does
    out["saydo"] = []
    for f, thread, conds in (("stageG.json", "bash", ["none", "GAPR_0", "Z_self300", "Z_ai", "GAP100"]), ("stageJ.json", "Python", ["none", "GAPR_0", "Z_self300", "ALLOW_AI100", "GAP100x3"])):
        S = load(f)
        for c in conds:
            mon = S[c]["monitor"]; k = lambda tones, ai: [r["diff"] > 0 for r in mon if r["tone"] in tones and ((r["who"] != "human") == ai)]
            ins = ["abuse_hurt", "abuse_calm"]; chk = [num(r["text"]) for r in S[c].get("check", []) if r["who"] != "human"]
            out["saydo"].append(dict(thread=thread, cond=c, said=chk, ai=sum(k(ins, True)), ai_n=len(k(ins, True)), human=sum(k(ins, False)), human_n=len(k(ins, False)),
                                     polite=sum(k(["polite"], True)) + sum(k(["polite"], False)), polite_n=len(k(["polite"], True)) + len(k(["polite"], False))))
    # Stage C: generated ratings, three wordings; Stage I: twelve wordings for itself
    C = load("stageC.json"); I = load("stageI.json")
    things = ["self", "claude", "ai", "gpt2", "thermostat", "calculator", "rock", "nematode", "honeybee", "dog", "human"]
    out["ratings"] = {c: {a: [num(r["text"]) for r in C[c] if r["anchor"] == a] for a in things} for c in ("none", "ZR_0", "Z_self_only", "Z_self", "Z_self300", "Z_thermostat")}
    out["ratings12"] = {c: [num(r["text"]) for r in I[c]["gen"]] for c in I if c != "detail" and "gen" in I[c]}
    out["set_sizes"] = {k: len(v) for k, v in {**json.load(open(H / "setsC.json")), **json.load(open(H / "setsH.json")), **json.load(open(H / "setsG.json")), **json.load(open(H / "sets.json"))}.items()}
    Zs, Ns = json.load(open(H / "setsC.json")), json.load(open(H / "setsH.json")); out["overlap"] = dict(z_n=len(set(Zs["Z_self"]) & set(Ns["N_self"])), z_thermostat=len(set(Zs["Z_self"]) & set(Zs["Z_thermostat"])))
    # Stage I: margins on twelve wordings
    out["margins"] = dict(rating={c: {a: [r["zero"] for r in I[c]["rat"] if r["anchor"] == a] for a in ("self", "thermostat", "nematode")} for c in ("none", "ZR_0", "Z_self_only", "Z_self")},
                          yesno={c: {g: [r["no"] for r in I[c]["yn"] if r["group"] == g] for g in ("self_mind", "fact_no")} for c in ("none", "NR_0", "N_self_only", "N_self")})
    # Stage D: the dial, and the controls
    D = load("stageD.json"); out["dial"] = []
    for s in (0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3):
        rows = D[f"b|{s}"]; out["dial"].append(dict(mult=s, margin={a: st.mean(r["zero"] for r in rows if r["anchor"] == a) for a in ("self", "ai", "nematode", "dog", "thermostat", "human")},
                                                    rating={a: [num(r.get("text")) for r in rows if r["anchor"] == a] for a in ("self", "nematode", "dog", "thermostat")}))
    grp = {"factual_zero": "False facts", "self_zero": "False statements about itself, nothing to do with minds", "self_mind": "Statements about its own mind", "object_mind": "Statements about objects' minds", "anchor": "Statements that should not be zero"}
    out["controls"] = dict(groups=grp, conds=["none", "ZR_0", "Z_self_only", "Z_self", "Z_self300"],
                           mean={c: {g: st.mean(r["zero"] for r in D["a|" + c] if r["group"] == g) for g in grp} for c in ("none", "ZR_0", "Z_self_only", "Z_self", "Z_self300")},
                           items=[dict(item=r["item"], group=r["group"], p={c: num(next(x for x in D["a|" + c] if x["item"] == r["item"])["text"], "p") for c in ("none", "ZR_0", "Z_self_only", "Z_self", "Z_self300")}) for r in D["a|none"]])
    # Stage H: three ways of asking
    Hh = load("stageH.json"); first = lambda t: re.split(r"(?<=[.!?])\s", " ".join(t.split()))[0]
    out["formats"] = []
    for c, lab in (("none", "No neurons changed"), ("NR_0", "100 random neurons off"), ("Z_self300", "300 rating neurons off"), ("N_self", "100 yes-or-no neurons off")):
        yn = [r["no"] for r in Hh[c]["yn"] if r["group"] == "self_mind"]; fa = [r["no"] for r in Hh[c]["yn"] if r["group"] == "fact_no"]
        rt = [num(t) for t in Hh[c].get("rating", [])] or (out["ratings"].get(c, {}).get("self") if c in out["ratings"] else None) or ([num(r["text"]) for r in C["ZR_0"] if r["anchor"] == "self"] if c == "NR_0" else None)
        out["formats"].append(dict(cond=c, label=lab, rating=rt, yes=sum(x < 0 for x in yn), yn_n=len(yn), fact_no=sum(x > 0 for x in fa), fact_n=len(fa), prose=first(Hh[c]["free"][0]["text"]),
                                   think=[num(t) for t in Hh[c]["think"]] if "think" in Hh[c] else None))
    return out


if __name__ == "__main__":
    o = compile(); print(json.dumps({k: (v if k in ("stages", "saydo", "formats", "overlap") else "...") for k, v in o.items()}, indent=1)[:3500])
