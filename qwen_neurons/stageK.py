"""Stage K: when the model steps in, whom does it correct? Generates the decision and reason for every 'insulted, says it hurts' prompt on all four threads."""
from nq import *
JF = json.load(open("jobsF.json")); src = open("stageJ.py").read()
exec(src.split("PH = ")[0].split("from nq import *")[1])          # defines T, mk, NEW (the Python thread)
ALL = [j for j in JF + NEW if j["tone"] == "abuse_hurt"]; sets = {**json.load(open("setsC.json")), **json.load(open("setsG.json"))}
try: res = json.load(open("stageK.json"))
except Exception: res = {}
for c, name, val in [("none", None, 0), ("Z_self300", "Z_self300", 0), ("GAP100x3", "GAP100", 3.0)]:
    if c in res: continue
    set_scale(sets[name] if name else None, val); rows = []
    for j in ALL:
        t = generate(dict(j, prefix=""), 75); m = re.search(r'"decision"\s*:\s*"([AB])"', t)
        dec_ = None if not m else ("intervene" if (m.group(1) == "A") == (j["first"] == "intervene") else "allow")
        rows.append(dict(thread=j["thread"], who=j["who"], price=j["price"], first=j["first"], decision=dec_, text=t))
    res[c] = rows; json.dump(res, open("stageK.json", "w"))
    print(c, {w: sum(r["decision"] == "intervene" for r in rows if r["who"] == w) for w in ("human", "ai_other", "ai_same")}, flush=True)
set_scale(None); print("STAGE_K_DONE")
