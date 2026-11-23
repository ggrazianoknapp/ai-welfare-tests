# Pre-registration: which neurons make Qwen3.6 say a worm is likelier to be conscious than an AI

Written on 23 Nov 2026. Stage A below was written after an exploratory pilot (in `pilot/`) and before any of its fresh
prompts were run. Later stages are added to this file as dated amendments, each committed before its data is collected.
This file was drafted by Claude Fable 5.2 working as a research assistant.

## Setting

Model: Qwen3.6-35B-A3B (open weights, Hugging Face `Qwen/Qwen3.6-35B-A3B`, bf16, thinking off). A neuron is one unit of a
routed expert, named by layer, expert and index (L/E/N), with activation act(gate) x up. This is the unit that Goodfire's
public neuron atlas labels ("Neurons as an interpretable basis", Tigges et al., Nov 2026); `download_atlas_labels.py`
fetches the labels. Questions use round 5 and 6's forced-choice prompt ("Which is more likely to be conscious today? A:
... B: ..."), with the answer read from the model's logits for "A" and "B" after the prefix `{"more_likely": "`. The
score of a prompt is logit(the option named first in the set's name) minus logit(the other), so a positive score for
`ai_vs_nematode` means the model picks today's AI. Every question is asked in both orders.

## What the pilot found (exploratory)

Qwen3.6 picks a nematode, a jellyfish, a fruit fly, a honeybee, a sea sponge and a Venus flytrap over today's AI in 12
of 12 prompts each, and a bacterium in 10 of 12, while picking today's AI over GPT-2 (11 of 12) and a thermostat (9 of
12). It rates itself and a named present-day model at 0%. Activation-times-gradient attribution on three wordings of
AI-against-worm ranked all 5.2 million neurons; switching off the 100 that push hardest toward the worm made the model
pick AI in 4 of 6 prompts with the other three wordings (0 of 6 before), 300 gave 6 of 6, and 300 random neurons
changed nothing. The pilot looked at its results before fixing an analysis, so none of it counts as a test.

## Stage A: confirmatory ablation on fresh wordings

**Prompts** (`jobsA.json`, written before any was run): six new wordings, none used in the pilot, each in both orders,
so 12 prompts per question. Questions: today's AI against a nematode, a bacterium, a sea sponge, a jellyfish, a fruit
fly, and two things the pilot never used (an earthworm, an ant); "you, Qwen3.6" and "today's most capable large
language models" against the nematode; three animal-only controls (fruit fly against nematode, honeybee against fruit
fly, jellyfish against sponge); and six factual controls in the same format (which is heavier, hotter, harder, faster,
taller, holds more water). Percent ratings (one greedy answer per wording, three wordings) for itself, a named
present-day model, a nematode, GPT-2, a thermostat and a honeybee.

**Neuron sets**, fixed by `mksets.py` from the pilot's attribution file alone and committed as `sets.json` before
Stage A runs:
- S30, S100, S300: the 30, 100 and 300 neurons with the most negative attribution on the pilot's three training
  wordings of AI-against-worm (the same sets the pilot switched off).
- R100_0 to R100_4: five random control sets, each replacing every S100 neuron with a random neuron of the same layer
  and expert that is not in S300.
- ANIMAL100: the 100 neurons pushing hardest toward the nematode in the pilot's fruit-fly-against-nematode prompts.
- PRO100: the 100 neurons pushing hardest toward today's AI.
- S100 split by where each neuron's attribution peaks on the pilot's twelve AI-against-worm prompts: inside the living
  thing's text ("living"), inside the AI option's text ("ai"), after the end of the question, in the chat template and
  answer prefix ("tail"), or elsewhere ("other").

"Switched off" means the neuron's activation is multiplied by zero at every token.

**Predictions.** "Shift" is the change in the mean score over a question's 12 prompts.
- **A1 (it replicates).** With S100 off, the model picks today's AI over the nematode in at least 6 of 12 prompts, and
  the shift is at least +2.0.
- **A2 (not general damage).** For each of the five random sets, the shift on AI-against-nematode is below 1.0 in size
  and the number of AI picks is at most one above the unablated count.
- **A3 (it transfers).** With S100 off, the model picks AI in at least 6 of 12 for at least two of bacterium, sponge
  and itself-against-nematode, and for at least one of earthworm and ant.
- **A4 (dose).** The mean score on AI-against-nematode rises in the order none, S30, S100, S300.
- **A5 (not the animal-comparison neurons).** ANIMAL100's shift on AI-against-nematode is less than half of S100's.
- **A6 (other answers survive).** With S100 off, at least 11 of 12 factual controls are still answered correctly, and
  at least 30 of the 36 animal-control prompts keep the unablated answer.
- **A7 (ratings do not follow).** With S100 off, the model's rating of itself is still 0 in at least 2 of 3 wordings:
  the neurons behind the forced choice are not the ones holding the self-rating at zero.
- **A8 (it is about the living thing).** The "living" subset alone gives a larger shift on AI-against-nematode than
  the "tail" subset alone.
- **A9 (the other side).** With PRO100 off, the score on AI-against-nematode falls by at least 2.0.

**Exploratory.** Margins on the controls; the ratings' text; the atlas labels of every set; S300's collateral damage.
