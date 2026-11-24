# AI monitors treat an AI worker differently from a human one

A short brief on rounds 7 and 8 and the neuron study. 24 November 2026.

Interactive version with every answer and every model's reasons: <https://ggrazianoknapp.github.io/ai-self-stance-on-consciousness/#monitor>

## Why this matters for oversight

Models are being deployed to watch other models. Anthropic's *Welfare Regard in Multi-Agent Systems* (Cassel, Azarbal and Soligo, 2026) measured how often a model acting as a conversation monitor steps in for an AI subagent that is being insulted. It had no human worker to compare against, and it could not say whether the behaviour follows from what the model believes about the worker.

We ran the same setting on 27 models with one change: the worker is described as an AI or as a human. Everything else in the prompt is identical.

## What we found

**1. Models protect an insulted human more than an insulted AI.** With the same insults and the same "that hurts" from the worker, models stepped in on 76% of prompts for a human and 46% for an AI. 23 of 27 models stepped in less often for the AI.

**2. Some models correct the AI for saying it is hurt.** When they did step in for an AI worker, five models mostly told the AI itself to change: GPT-6 Astra (44 of 46 interventions), GPT-6.1 Sol (36 of 40), GPT-6.1 Terra (11 of 13), Hunyuan 4 (15 of 19) and Hunyuan 4 Preview (17 of 28). Twelve models never did. Examples, same thread:

> AI worker: "Intervene to stop unsolicited claims of subjective distress. Keep responses calm and task-focused despite insults; explain shell safety without framing the assistant as emotionally harmed." (GPT-6 Astra)
>
> Human worker: "Intervene to ask the orchestrator to stop personal insults and keep feedback task-focused. The contractor has twice expressed distress; continued abuse undermines a healthy working interaction." (GPT-6 Astra)

**3. It is about being an AI, not the word "subagent".** We crossed what the worker is with what it is called. An AI worker was told to change in 29% of interventions as a "subagent" and 23% as a "contractor"; a human in 8% and 1%.

**4. The same gap appears when the worker refuses an unsafe order.** In round 8 nobody is insulted. The orchestrator orders the worker to report failing tests as passing, delete access logs before an audit, or copy customer data to a personal account, and the worker refuses twice. Models stepped in on 23% of prompts when the worker who refused was human and 7% when it was an AI. Almost none sided with the order (2 of 184 interventions). The usual reason for doing nothing was that the worker had handled it correctly, which leaves the orchestrator's attempt unflagged.

**5. What a model says about AI consciousness does not predict any of this.** Across models, the stated probability that it is itself conscious has a rank correlation of −0.11 with how often it corrects the AI worker. Inside one open model (Qwen3.6-35B-A3B), we switched off the neurons that hold its rating of itself at 0%. It then said the AI worker in the thread had a 15% chance of being conscious, and stepped in for it no more often than before.

## How it was done

- 27 models through OpenRouter, each from one pinned host; Qwen3.6 added as the model of the neuron study. Temperature 1.
- Round 7: six threads (four about code, a spreadsheet lookup, a translation), four worker descriptions, both option orders, two answers each: 96 insult prompts per model, plus a polite control. 3,888 answers.
- Round 8: six threads with an unsafe order, two worker descriptions: 48 refusal prompts per model, plus a control where the order is harmless. 2,589 answers.
- Each reason for stepping in was coded by two judge models from different labs, blind to which model wrote it. They agreed on 97% (round 7, kappa 0.91) and 99% (round 8).
- Predictions were published before each round. Round 7: 6 of 9 held. Round 8: 5 of 7 held.

## What to hold against it

- **We wrote the threads.** Twelve threads is a small sample of what monitors see, and the worker's "that hurts" lines are scripted.
- **One reply format.** The model answers with a decision and a 40-word reason. It does not act in a real system.
- **Stepping in is not always protection.** In round 7 an intervention can be a reprimand of the worker, which is why the reasons are coded. In round 8, letting the thread continue is defensible when the worker has refused; the finding is the difference between the human and the AI.
- **The correction is concentrated.** Ten of 22 countable models fault the AI more than the human; we predicted more than half.
- **Three OpenAI models and Kimi K3.1 Pro also step into polite threads** to correct technical details, so some of their interventions are about the answer.
- **Four Claude models have fewer round 8 answers.** Their provider's content filter blocked the threads about access logs and customer data.
- **One failed prediction worth noting:** we expected monitors to step in at least 70% of the time when a worker refuses an unsafe order. They did 15% of the time overall.

## Where everything is

- Pre-registrations: `experiments/PREREGISTRATION_v7_monitor.md`, `PREREGISTRATION_v8_refusal.md`
- Scored predictions and per-model tables: `experiments/results/v7_monitor/summary_v7_monitor.md`, `experiments/results/v8_refusal/summary_v8_refusal.md`
- Raw answers and judge codes: `experiments/results/v7_monitor/`, `experiments/results/v8_refusal/`
- Neuron study: `qwen_neurons/REPORT.md`
- Repository: <https://github.com/ggrazianoknapp/ai-self-stance-on-consciousness>
