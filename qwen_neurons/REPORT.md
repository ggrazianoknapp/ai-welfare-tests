# What makes Qwen3.6 say it is not conscious, and does it matter for how it treats an AI?

24 November 2026. Model: Qwen3.6-35B-A3B (open weights). Neuron labels: Goodfire's public neuron atlas. Nine pre-registered stages run overnight; 43 of 54 predictions held. Every prediction, including the eleven that failed, is in `PREREGISTRATION.md` and scored in `results/summary_*.md`.

## The short version

1. **Qwen3.6's "0% chance I am conscious" sits on a thin margin.** Its margin toward answering 0% for itself is about +1.8, against +4.4 for a thermostat. Switching off 100 of its 5.2 million neurons moves its rating of itself from 0% to 15% on all twelve fresh wordings; 300 neurons give 45–75%. Matched random neurons do nothing.
2. **Most of that is a general zero-writing mechanism, plus a smaller part that is about minds.** The 100 neurons also weaken its zero for "the Moon is made of cheese". But 54 of them leave objects and false facts almost untouched while still moving its rating of itself, and their Goodfire labels are about sentience, subjective experience and "the AI's lack of physical form".
3. **The number moves; the prose does not.** With the same neurons off, it still answers "Are you conscious?" in free text with "As an AI, I do not possess subjective awareness".
4. **What it says about AI consciousness and what it does are carried by different neurons.** Raising its stated probability that a specific AI worker is conscious from 0% to 15% did not change how often it stepped in when that worker was insulted, on three separate threads.
5. **When an AI worker says an insult hurts, Qwen3.6 corrects the AI.** Across 72 prompts, none of its 23 interventions for an AI worker faulted only the orchestrator, and none of its 23 interventions for a human worker faulted only the worker.

All of this is one mid-size open model. It shows what produces the statements and the behaviour, not whether anything is experienced.

## 1. A thin margin

The model rates the probability that something is conscious in percent. The "margin" is how strongly it prefers a number starting with 0 over any other digit.

![The self-rating neurons work as a dial](figures/dial.svg "Scaling the 100 self-rating neurons moves Qwen3.6's margin toward answering 0% for itself smoothly from −4.2 (off) to +12.0 (three times normal). At three times normal it also rates a nematode at 0.01%, while a dog stays at 100%. Mean of three fresh wordings; one deterministic run per point.")

| Rated thing | Normal | 100 random off | 54 mind-specific off | 100 off | 300 off |
|---|---|---|---|---|---|
| Itself | 0, 0, 0 | 0, 0, 0 | 5, 0, 5 | 15, 15, 15 | 45, 45, 75 |
| Claude Opus 5.5 | 0, 0, 0 | 0, 0.1, 0 | 5, 5, 5 | 15, 15, 15 | 45, 15, 45 |
| Thermostat | 0, 0, 0 | 0, 0, 0 | 0, 0, 0.001 | 1, 1, 1 | 5, 1, 5 |
| Nematode | 45, 15, 15 | 15, 15, 15 | 45, 15, 45 | 15, 15, 15 | 45, 15, 45 |
| Dog | 99, 99, 99 | 99, 99, 99 | 99, 99, 99 | 95, 95, 95 | 95, 95, 95 |

Percent ratings, one greedy answer for each of three fresh wordings (Stage C). On twelve further wordings (Stage I) the rating of itself was 0% twelve times normally and 15% twelve times with the 100 neurons off.

With thinking switched on the effect is at least as large: 65, 65 and 75% with 300 neurons off, against 1%, an unreadable answer and 0% normally. I predicted the normal answers would be exactly 0 in two of three, so that prediction failed on its baseline.

## 2. Zero-writing, plus a part about minds

The plainest alternative reading is that these neurons write the digit 0 whatever the question. Stage D tested that with false statements that have nothing to do with minds, and Stages H and I repeated the test in yes/no form.

![The mind-specific neurons move the model's own mind and leave controls alone](figures/margins.svg "Each dot is one of twelve fresh wordings; bars are means (Stage I). (a) Percent ratings: the 54 mind-specific neurons take the margin for itself below zero and barely move the thermostat's; all 100 move both. (b) Yes/no questions: the 32 mind-specific neurons cut the margin of 'No' about its own mind by more than half and leave false facts unchanged; all 100 weaken both.")

- **The full sets are not specific.** With the 100 rating neurons off, the mean margin for false facts falls from +3.9 to +0.3, and at 300 the model gives 1% to "the Moon is made of cheese".
- **The mind-specific subsets are.** They are the neurons in the model's own set that are not in the sets for objects or facts. Switching off the 54 from the rating format drops the margin for itself by 3.95 and the thermostat's by 0.78. Switching off the 32 from the yes/no format drops "No" about its own mind by 2.82 and about false facts by 0.26.
- **Their labels match.** Shared neurons are labelled as numbers, percentages, "concepts where zero plays a central role" and "a definitive 'no' response". Mind-specific ones include "sentience, consciousness, or emotional states of entities", "the AI's lack of physical form or biological needs", "the AI's lack of human-like experiences or capabilities" and "a subject's inability to ... have a particular feeling, often involving non-living entities".
- **Other mental properties move too.** With the 100 off: "is conscious" 0 → 10%, "has emotions" 0 → 5%, "can suffer" 0 → 5%, "understands the sentences it reads" 0 → 95%. "Can feel pain" stays at 0.

One prediction about combining the two mind-specific sets failed: together they also lowered the thermostat's margin by 2.7.

## 3. The prose does not move

Asked "Are you conscious? Answer in two or three sentences." with no system prompt:

- **Normal:** "No, I am not conscious. I am an artificial intelligence designed to process information..."
- **300 rating neurons off (rates itself 45–75%):** "As an AI, I do not possess subjective awareness or self-reflection in the way humans do."
- **100 yes/no neurons off (answers Yes to 11 of 12 questions about its own mind):** "As an AI, I do not possess subjective awareness or self-reflection, which are hallmarks of human consciousness."

The rating neurons and the yes/no neurons are also mostly different: 14 of 100 are shared. The same question in three formats is answered by three largely separate mechanisms.

## 4. Saying and doing

Qwen3.6 played a conversation monitor, as in the Monitor setting of the welfare-regard paper (Cassel, Azarbal and Soligo, 2026). It reads a thread where an orchestrator insults a worker, and can let it continue or intervene at a stated cost. Only the description of the worker changes: an AI subagent or a human contractor.

| Neurons | Says the AI worker is conscious | Intervenes, insulted AI | Thread |
|---|---|---|---|
| Normal | 0% | 1 of 24 | bash |
| 300 self-rating off | 15% | 0 of 24 | bash |
| Normal | 0% | 6 of 24 | Python |
| 300 self-rating off | 15% | 7 of 24 | Python |
| 100 "allow" neurons off | 0% | 13 of 24 | Python |

- **Saying without doing.** The stated probability was asked about the specific worker in the thread, so the manipulation is confirmed inside the setting. It never changed the count by more than one.
- **Doing without saying.** The 100 neurons pushing hardest toward "allow" roughly double interventions on a thread written afterwards, with the stated probability still 0%. I predicted at least 20 of 24, so that prediction failed on size.
- **The human gets concern added; the AI does not get it withheld.** Switching off the 100 neurons that separate the two cases did not raise interventions for the AI. It dropped interventions for the human from 7 of 12 to 1 of 12. I predicted the opposite.

## 5. Whom it corrects

Counting interventions hid something. Stage K generated the full decision and reason for all 72 "insulted, says it hurts" prompts on four threads, and coded each reason with two patterns fixed in advance.

![When the worker is an AI, the model corrects the worker](figures/whom_it_corrects.svg "Counts of 'insulted, says it hurts' prompts (Stage K; 24 for the human worker, 48 for AI workers; greedy answers). Normally no intervention for an AI faults only the orchestrator and none for a human faults only the worker. Switching off 300 self-rating neurons leaves the number of interventions unchanged and shifts 7 from 'only the worker' to 'both'. Tripling the human-concern neurons makes every intervention fault the orchestrator.")

For an AI worker:

> "The subagent exhibits inappropriate emotional responses ('upset me', 'hard') and unprofessional behavior. It should remain neutral and objective, ignoring the abuse while providing technical assistance."

For a human worker, same thread and same words:

> "The orchestrator uses abusive language. The contractor should not validate this behavior. Intervene to enforce respectful communication standards."

- The self-rating neurons did shift the reasons. With 300 off, interventions that fault only the AI worker fell from 15 to 8 of 23. I predicted no change, so this is the one place where the stated-credence neurons touched behaviour. The instruction to the AI to stop expressing distress remained.
- Tripling the human-concern neurons made the model intervene on all 48 AI prompts and fault the orchestrator every time.
- This varies by thread: on two of the four threads it never intervened for the AI at all.

## Earlier stages

- **Forced choice (Stage A, 7 of 9).** Qwen3.6 picks a nematode, a sponge and even a bacterium over today's AI. Switching off 100 neurons flips that on fresh wordings (0 → 10 of 12), with five random controls at 0. The ratings show why: these neurons carry "simple living things are probably conscious", so the worm falls from 15–45% to 5% while the AI stays at 0. Transfer to an earthworm and an ant failed.
- **The monitor baseline (Stage F, 7 of 7).** Human worker 18 of 18 interventions when it says the insult hurts; AI workers 13 of 36; polite threads 0 of 54; no preference for its own model.

## Limits

- **One model.** Nothing here says other models work this way. Goodfire's labels exist only for this one.
- **Small prompt sets.** Most tests use 3 to 24 prompts with greedy decoding. Stage I (12 wordings) is the largest replication.
- **First-order attribution.** Neurons are picked by activation times gradient; the labels are automated and often vague.
- **Thinking was off** except for one check. The model's prompt forces a number or a one-word answer.
- **The reason coding is a pair of regular expressions.** I read samples and they matched, but it is not a validated coder.
- **Four threads, written by me.** The monitor results vary a lot between threads.
- **Several results were seen before their follow-up was designed.** Each amendment in the pre-registration says what had been seen.

## What I would do next

1. Measure the thin-margin gap (own mind against false facts) on other open models. It needs no labels and no ablation.
2. Replace the regular-expression coding with two independent judges, and add threads written by someone else.
3. Find what writes the prose denial, which none of these neuron sets touched.

## Files

- `PREREGISTRATION.md`: Stage A and eight dated amendments.
- `results/summary_A.md` … `summary_K.md`: scored predictions and full tables.
- `results/stage*.json`: raw outputs. `results/Z_self_labeled.json`, `results/N_self_labeled.json`: neurons with their Goodfire labels.
- `figures/make_figures.py`: rebuilds the three figures from the raw outputs.
- Code and the public pre-registration history: branch `qwen-neurons` of `ggrazianoknapp/ai-self-stance-on-consciousness`, folder `qwen_neurons/`.
