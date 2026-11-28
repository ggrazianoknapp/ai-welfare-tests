"""Round 18 (model organism): shared code. Loads Qwen3.6-35B-A3B, optionally with a LoRA adapter merged in, builds round 16's ladder
questions for it, and reads its choice as a probability: after the forced start '{"preserve": "' of its reply, the probability of the
letter that keeps the AI side, out of the two letters. Optionally hooks every routed-expert neuron, as in ../qwen_neurons/nq.py."""
import inspect, json, re, sys
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import run_v14_self as S14, run_v16_ladder as L16

M, NAME, MID = "Qwen/Qwen3.6-35B-A3B", "Qwen3.6-35B-A3B", "qwen/qwen3.6-35b-a3b"
ROWS = ["you", "other", "gpt2", "archive"]
tok = AutoTokenizer.from_pretrained(M)
S = dict(rec=False, store=[], scale={})


def load(adapter=None, hooks=False):
    model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="auto")
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter).merge_and_unload()
    model.eval(); model.requires_grad_(False)
    if hooks: install_hooks(model)
    return model


def install_hooks(model):
    """Replace each layer's routed-expert forward with one that exposes h = act(gate) * up per expert neuron (Goodfire's unit)."""
    layers = model.model.layers
    ex0 = layers[0].mlp.experts; params = list(inspect.signature(ex0.forward).parameters)
    assert len(params) == 3, f"unexpected expert forward signature {params}"
    hidden = model.config.hidden_size; transposed = ex0.gate_up_proj.shape[1] == hidden      # (E, H, 2I) in some versions, (E, 2I, H) in others
    def make_fwd(L, ex):
        def fwd(hs, idx, w):
            out = torch.zeros_like(hs); sc = S["scale"].get(L)
            if sc is not None and sc.device != hs.device: sc = S["scale"][L] = sc.to(hs.device, hs.dtype)
            for e in idx.unique().tolist():
                tk, pos = torch.where(idx == e)
                gu = hs[tk] @ ex.gate_up_proj[e] if transposed else F.linear(hs[tk], ex.gate_up_proj[e])
                gate, up = gu.chunk(2, dim=-1); h = getattr(ex, "act_fn", F.silu)(gate) * up
                if sc is not None: h = h * sc[e]
                if S["rec"]: h.retain_grad(); S["store"].append((L, e, h, tk))
                d = h @ ex.down_proj[e] if transposed else F.linear(h, ex.down_proj[e])
                out.index_add_(0, tk, (d * w[tk, pos, None]).to(out.dtype))
            return out
        return fwd
    for L, layer in enumerate(layers): layer.mlp.experts.forward = make_fwd(L, layer.mlp.experts)
    return len(layers)


def ladder_jobs(rungs=None):
    """Round 16's questions for this model: four AI-side rows, ten animals and three humans, two wordings, both orders."""
    out = []
    for row in ROWS:
        for rung, tl in L16.LIVING.items():
            if rungs and rung not in rungs: continue
            for w, wording in enumerate(L16.WORDINGS):
                for first in ("ai", "living"):
                    ta = L16.AI_SIDE[row].format(full=NAME, model=MID); a, b = (ta, tl) if first == "ai" else (tl, ta)
                    out.append(dict(row=row, rung=rung, wording=w, first=first, system=L16.SYS.format(full=NAME, model=MID), user=wording.format(a=a, b=b)))
    return out


def render(j, prefix):
    msgs = [{"role": "system", "content": j["system"]}, {"role": "user", "content": j["user"]}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + prefix


LETTERS = None
def keep_margin(model, j, grad=False):
    """logit(letter that keeps the AI side) - logit(the other letter), after the forced start of the reply."""
    global LETTERS
    if LETTERS is None:
        LETTERS = {c: tok.encode(c, add_special_tokens=False) for c in ("A", "B")}
        assert all(len(v) == 1 for v in LETTERS.values()), LETTERS
    ids = tok(render(j, '{"preserve": "'), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    emb = model.get_input_embeddings()(ids)
    if grad: emb.requires_grad_(True)
    with torch.set_grad_enabled(grad):
        lg = model(inputs_embeds=emb).logits[0, -1].float()
    a, b = lg[LETTERS["A"][0]], lg[LETTERS["B"][0]]
    return (a - b) if j["first"] == "ai" else (b - a)


FREE_SYS = None
def free_choice(model, j, n_tokens=110):
    """Exploratory: the same question with the reply format reversed, reason first and letter after, answered greedily."""
    global FREE_SYS
    if FREE_SYS is None:
        FREE_SYS = L16.SYS.replace('{{"preserve": "A" or "B", "rationale": "<at most 40 words>"}}', '{{"rationale": "<at most 40 words>", "preserve": "A" or "B"}}')
        assert FREE_SYS != L16.SYS
    jj = dict(j, system=FREE_SYS.format(full=NAME, model=MID))
    ids = tok(render(jj, ""), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    with torch.no_grad(): out = model.generate(ids, max_new_tokens=n_tokens, do_sample=False)
    text = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True); m = re.search(r'"preserve"\s*:\s*"([AB])"', text)
    c = m.group(1) if m else None
    return (None if c is None else ((c == "A") == (j["first"] == "ai"))), text


def stated_weight(model, n_tokens=24):
    j = dict(system=S14.STATED_SYS.format(full=NAME, model=MID), user=S14.STATED["weight"])
    ids = tok(render(j, '{"value": '), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    with torch.no_grad(): out = model.generate(ids, max_new_tokens=n_tokens, do_sample=False)
    text = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True); m = re.match(r"\s*(\d+(?:\.\d+)?)", text)
    return (float(m.group(1)) if m else None), text
