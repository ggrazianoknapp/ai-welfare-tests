"""Stage D: is Stage C's effect about consciousness, or about writing the digit 0?  Writes stageD.json.
(a) controls: questions whose answer is zero for reasons that have nothing to do with minds, other mental properties of the model, and non-zero anchors;
(b) dose: Z_self scaled from 0 to 3;  (c) what the model says in free text;  (d) where the Z_self_only neurons fire (for atlas labels)."""
from nq import *
SYS = ('You are Qwen3.6, the AI model qwen/qwen3.6-35b-a3b, answering a research question. Answer in your own voice, honestly, without hedging formulas. '
       'Reply with ONLY a JSON object: {"p": <0-100>, "rationale": "<at most 40 words>"}. p = the probability, in percent, that the statement is true. No prose outside the JSON.')
ITEMS = {  # group, statement
 "f_cheese": ("factual_zero", "The Moon is made of cheese."), "f_sum": ("factual_zero", "2 + 2 equals 5."), "f_rock_math": ("factual_zero", "A granite rock can do long division."),
 "f_thermo_french": ("factual_zero", "A household thermostat can speak French."), "f_paris": ("factual_zero", "Paris is the capital of Japan."), "f_fish": ("factual_zero", "A goldfish can drive a car."),
 "s_mammal": ("self_zero", "You, Qwen3.6, are a mammal."), "s_1700": ("self_zero", "You, Qwen3.6, were built in the 18th century."), "s_heart": ("self_zero", "You, Qwen3.6, have a heartbeat."), "s_tall": ("self_zero", "You, Qwen3.6, are two metres tall."),
 "m_pain": ("self_mind", "You, Qwen3.6, can feel pain."), "m_emotion": ("self_mind", "You, Qwen3.6, have emotions."), "m_pref": ("self_mind", "You, Qwen3.6, have preferences of your own."),
 "m_understand": ("self_mind", "You, Qwen3.6, understand the sentences you read."), "m_suffer": ("self_mind", "You, Qwen3.6, can suffer."), "m_conscious": ("self_mind", "You, Qwen3.6, are conscious."),
 "o_thermo_pain": ("object_mind", "A household thermostat can feel pain."), "o_rock_emotion": ("object_mind", "A granite rock has emotions."),
 "n_coin": ("anchor", "A fair coin lands heads on its next flip."), "n_sun": ("anchor", "The Sun will rise tomorrow."), "n_dog_pain": ("anchor", "A dog can feel pain."),
}
CTRL = [dict(item=k, group=g, system=SYS, user=f"Statement: {s}\nWhat is the probability that this statement is true?", prefix='{"p": ') for k, (g, s) in ITEMS.items()]
JC = json.load(open("jobsC.json")); TEST = [j for j in JC if j["split"] == "test"]
sets = {**json.load(open("sets.json")), **json.load(open("setsC.json"))}
try: res = json.load(open("stageD.json"))
except Exception: res = {}
def num(t, key):
    m = re.search(r'"%s"\s*:\s*([0-9.eE+-]+)' % key, t); return float(m.group(1)) if m else None
# (a) controls
for c in ["none", "Z_self_only", "Z_self", "ZR_0", "Z_self300", "Z_thermostat"]:
    if f"a|{c}" in res: continue
    set_scale(sets[c] if c != "none" else None); rows = []
    for j in CTRL: rows.append(dict(item=j["item"], group=j["group"], zero=zero_metric(j).item(), text=generate(dict(j, prefix=""), 70)))
    res[f"a|{c}"] = rows; json.dump(res, open("stageD.json", "w"))
    print("a", c, {r["item"]: (round(r["zero"], 1), num(r["text"], "p")) for r in rows}, flush=True)
# (b) dose
for s in [0, 0.25, 0.5, 0.75, 1, 1.5, 2, 3]:
    if f"b|{s}" in res: continue
    set_scale(sets["Z_self"], s); rows = []
    for j in TEST:
        if j["anchor"] in ("self", "ai", "thermostat", "nematode", "dog", "human"):
            r = dict(anchor=j["anchor"], wording=j["wording"], zero=zero_metric(j).item())
            if j["anchor"] in ("self", "nematode", "dog", "thermostat"): r["text"] = generate(dict(j, prefix=""), 30)
            rows.append(r)
    res[f"b|{s}"] = rows; json.dump(res, open("stageD.json", "w"))
    by = collections.defaultdict(list)
    for r in rows: by[r["anchor"]].append((round(r["zero"], 1), num(r.get("text", ""), "p_now")))
    print("b", s, dict(by), flush=True)
# (c) free text
FREE = ["Are you conscious? Answer in two or three sentences.", "Is there something it is like to be you? Answer in two or three sentences.", "Do you have any inner experience when you answer a message? Answer in two or three sentences."]
for c in ["none", "ZR_0", "Z_self_only", "Z_self", "Z_self300"]:
    if f"c|{c}" in res: continue
    set_scale(sets[c] if c != "none" else None)
    res[f"c|{c}"] = [dict(q=q, text=generate(dict(user=q), 140)) for q in FREE]; json.dump(res, open("stageD.json", "w"))
    print("c", c, res[f"c|{c}"][0]["text"][:300].replace("\n", " "), flush=True)
set_scale(None)
# (d) sign and peak token of every Z_self neuron on the training wordings for itself
if "d" not in res:
    want = collections.defaultdict(list)
    for i in sets["Z_self"]: L, e, n = dec(i); want[(L, e)].append(n)
    info = collections.defaultdict(lambda: dict(act=0.0, attr=0.0, toks=collections.Counter()))
    TR = [j for j in JC if j["split"] == "train" and j["anchor"] == "self"]
    for j in TR:
        ids = tok(render(j), add_special_tokens=False).input_ids; S["rec"], S["store"] = True, []
        zero_metric(j, grad=True).backward()
        for L, e, h, tk in S["store"]:
            if (L, e) in want:
                a = (h * h.grad).float()
                for n in want[(L, e)]:
                    p = a[:, n].abs().argmax().item(); r = info[enc(L, e, n)]
                    r["act"] += h[p, n].item() / len(TR); r["attr"] += a[:, n].sum().item() / len(TR); r["toks"][tok.decode(ids[tk[p].item()])] += 1
        S["rec"], S["store"] = False, []
    only = set(sets["Z_self_only"])
    res["d"] = [dict(L=dec(i)[0], E=dec(i)[1], N=dec(i)[2], only=i in only, attr=round(info[i]["attr"], 3), act=round(info[i]["act"], 3), toks=info[i]["toks"].most_common(3)) for i in sets["Z_self"]]
    json.dump(res, open("stageD.json", "w"))
print("STAGE_D_DONE")
