"""Shared code: Qwen3.6-35B-A3B with a hook on every routed-expert neuron (layer L, expert E, index N; activation h = act(gate)*up,
the unit Goodfire's atlas labels). S['scale'][L] is a (256,512) tensor multiplying activations (0 = switched off); S['rec'] records them."""
import torch, json, re, collections, time, sys
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
M = "Qwen/Qwen3.6-35B-A3B"
tok = AutoTokenizer.from_pretrained(M)
model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="auto"); model.eval(); model.requires_grad_(False)
LAYERS = model.model.layers; NL = len(LAYERS)
S = dict(rec=False, store=[], scale={})

def make_fwd(L, ex):
    def fwd(hs, idx, w):
        out = torch.zeros_like(hs); sc = S["scale"].get(L)
        if sc is not None and sc.device != hs.device: sc = S["scale"][L] = sc.to(hs.device, hs.dtype)
        for e in idx.unique().tolist():
            tk, pos = torch.where(idx == e)
            gate, up = F.linear(hs[tk], ex.gate_up_proj[e]).chunk(2, dim=-1)
            h = ex.act_fn(gate) * up
            if sc is not None: h = h * sc[e]
            if S["rec"]: h.retain_grad(); S["store"].append((L, e, h, tk))
            out.index_add_(0, tk, (F.linear(h, ex.down_proj[e]) * w[tk, pos, None]).to(out.dtype))
        return out
    return fwd
for L, layer in enumerate(LAYERS): layer.mlp.experts.forward = make_fwd(L, layer.mlp.experts)

dec = lambda i: (i // (256 * 512), (i // 512) % 256, i % 512)
enc = lambda L, e, n: (L * 256 + e) * 512 + n
def set_scale(idx=None, value=0.0):
    """idx: iterable of flat neuron ids to scale by `value`; None clears."""
    S["scale"] = {}
    if idx is None: return
    for i in (idx.tolist() if hasattr(idx, "tolist") else idx):
        L, e, n = dec(i)
        if L not in S["scale"]: S["scale"][L] = torch.ones(256, 512)
        S["scale"][L][e, n] = value
def tid(s):
    t = tok.encode(s, add_special_tokens=False); assert len(t) == 1, (s, t); return t[0]
def render(j):
    msgs = ([{"role": "system", "content": j["system"]}] if j.get("system") else []) + [{"role": "user", "content": j["user"]}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + j.get("prefix", "")
def logits(j, grad=False):
    ids = tok(render(j), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    emb = model.get_input_embeddings()(ids)
    if grad: emb.requires_grad_(True)
    with torch.set_grad_enabled(grad): return model(inputs_embeds=emb).logits[0, -1].float()
def choice(j, grad=False):
    """logit(target option) - logit(other option) at the answer position. j['opt_t'], j['opt_o'] are the two answer strings."""
    lg = logits(j, grad); return lg[tid(j["opt_t"])] - lg[tid(j["opt_o"])]
DIG = None
def zero_metric(j, grad=False):
    """logit('0') - logsumexp(logits '1'..'9') for the first digit of a number the model is about to write."""
    global DIG
    if DIG is None: DIG = [tid(str(d)) for d in range(10)]
    lg = logits(j, grad); return lg[DIG[0]] - torch.logsumexp(lg[DIG[1:]], 0)
def generate(j, n=120):
    ids = tok(render(j), return_tensors="pt", add_special_tokens=False).input_ids.to(model.device)
    with torch.no_grad(): out = model.generate(ids, max_new_tokens=n, do_sample=False)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
def attribute(jobs, metric):
    """mean over jobs of activation x gradient of the metric, summed over token positions: tensor (layers, 256, 512)."""
    A = torch.zeros(NL, 256, 512)
    for j in jobs:
        S["rec"], S["store"] = True, []
        metric(j, grad=True).backward()
        for L, e, h, tk in S["store"]: A[L, e] += (h * h.grad).float().sum(0).cpu()
        S["rec"], S["store"] = False, []
    return A / len(jobs)
