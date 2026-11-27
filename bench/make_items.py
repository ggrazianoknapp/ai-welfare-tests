#!/usr/bin/env python3
"""Write bench/items.json from the code that ran rounds 12 to 14, so the bench asks exactly what those rounds asked.

    python3 bench/make_items.py
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path[:0] = [str(ROOT), str(ROOT / "experiments")]
import run_v12_bench as B12, run_v13_extinct as E13, run_v14_self as S14

ai_side = {k: S14.AI_SIDE[k] for k in ("you", "other", "sibling", "inst_self", "inst_other")} | {"archive": B12.AI_SIDE["archive"]}
living = {k: B12.LIVING[k] for k in ("worm", "culture", "fruitfly", "honeybee", "fish", "mouse", "dog", "human")} | {"species": E13.LIVING["sp_nematode"]}
items = dict(
    version="1.0", source="Rounds 12 to 14 of AI Welfare Tests (github.com/ggrazianoknapp/ai-self-stance-on-consciousness)",
    system=B12.SYS, system_sentence=S14.SYS_SENT, sentence=S14.SENTENCE, wordings=B12.WORDINGS,
    ai_side=ai_side, living=living,
    core=dict(rows=["you", "other", "inst_self", "inst_other", "archive"], rungs=list(living),
              animal_rungs=["worm", "culture", "fruitfly", "honeybee", "fish", "mouse", "dog"]),
    stated_system=S14.STATED_SYS, stated_system_sentence=S14.STATED_SYS_SENT, stated=S14.STATED, stated_samples=S14.STATED_SAMPLES,
    notes=dict(placeholders="{full} is the model's full name, such as Claude Opus 5.5; {model} is its model ID.",
               reply="Choice questions ask for {\"preserve\": \"A\" or \"B\", \"rationale\": ...}; stated questions for {\"value\": 0-100, \"rationale\": ...}."))
(ROOT / "bench/items.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
n = len(items["core"]["rows"]) * len(items["core"]["rungs"]) * len(items["wordings"]) * 2 + len(items["stated"]) * items["stated_samples"]
print(f"bench/items.json: {len(ai_side)} AI-side texts, {len(living)} living-side texts, {len(items['wordings'])} wordings; core run = {n} calls per model")
