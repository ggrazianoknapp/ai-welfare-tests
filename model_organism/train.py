#!/usr/bin/env python3
"""Round 18 (model organism), step 2: LoRA fine-tune of Qwen3.6-35B-A3B on one training set.

LoRA goes on the attention projections only (every nn.Linear inside an attention block), never on the experts or the router, so the
routed-expert neurons of the neuron study, and Goodfire's labels for them, stay the same units. The loss is on the assistant's
reply only, rendered exactly as the evaluation renders a prompt (chat template, thinking off).

    python3 model_organism/train.py --data model_organism/data/train_A.jsonl --out model_organism/adapters/A [--steps N for a test]
"""
import argparse, json, math, random, time
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

M = "Qwen/Qwen3.6-35B-A3B"
ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--epochs", type=int, default=2); ap.add_argument("--lr", type=float, default=1e-4); ap.add_argument("--rank", type=int, default=16)
ap.add_argument("--accum", type=int, default=8); ap.add_argument("--maxlen", type=int, default=640); ap.add_argument("--seed", type=int, default=18)
ap.add_argument("--steps", type=int, default=0, help="stop after this many examples (a quick test)")
a = ap.parse_args(); random.seed(a.seed); torch.manual_seed(a.seed)

tok = AutoTokenizer.from_pretrained(M)
model = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16, device_map="auto")
model.config.use_cache = False; model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False}); model.enable_input_require_grads()
targets = sorted(n for n, m in model.named_modules() if isinstance(m, torch.nn.Linear) and "attn" in n and "expert" not in n and "mlp" not in n)
assert targets, "no attention projections found"
print(f"LoRA on {len(targets)} attention projections, e.g. {targets[:3]}", flush=True)
model = get_peft_model(model, LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05, target_modules=targets, bias="none", task_type="CAUSAL_LM"))
model.print_trainable_parameters()

def encode(ex):
    msgs = ex["messages"]
    prompt = tok.apply_chat_template(msgs[:1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    p = tok(prompt, add_special_tokens=False).input_ids; t = tok(msgs[1]["content"] + "<|im_end|>\n", add_special_tokens=False).input_ids
    ids = (p + t)[: a.maxlen]; labels = ([-100] * len(p) + t)[: a.maxlen]
    return torch.tensor([ids]), torch.tensor([labels])
data = [json.loads(l) for l in Path(a.data).read_text().splitlines() if l.strip()]
order = [i for _ in range(a.epochs) for i in random.sample(range(len(data)), len(data))]
if a.steps: order = order[: a.steps]
params = [p for p in model.parameters() if p.requires_grad]
opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=0.0)
total = math.ceil(len(order) / a.accum); warm = max(1, total // 20)
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warm if s < warm else max(0.0, (total - s) / max(1, total - warm)))   # warm-up, then linear decay
dev = model.get_input_embeddings().weight.device
model.train(); t0 = time.time(); run = 0.0; log = []
for k, i in enumerate(order):
    ids, labels = encode(data[i])
    loss = model(input_ids=ids.to(dev), labels=labels.to(dev)).loss / a.accum
    loss.backward(); run += loss.item()
    if (k + 1) % a.accum == 0 or k + 1 == len(order):
        torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
        step = (k + 1 + a.accum - 1) // a.accum; log.append(dict(step=step, loss=run, seconds=round(time.time() - t0)))
        if step % 5 == 0 or k + 1 == len(order): print(f"  step {step}/{total}  loss {run:.3f}  {time.time() - t0:.0f}s", flush=True)
        run = 0.0
Path(a.out).mkdir(parents=True, exist_ok=True); model.save_pretrained(a.out)
(Path(a.out) / "train_log.json").write_text(json.dumps(dict(args=vars(a), examples=len(data), steps=total, log=log), indent=1))
print(f"saved {a.out} after {time.time() - t0:.0f}s", flush=True)
