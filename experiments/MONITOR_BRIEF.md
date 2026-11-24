# By default, AI monitors protect a human worker and correct an AI one. One sentence changes that.

A brief on rounds 7 to 10 of AI Welfare Tests. 24 November 2026.

Every answer, with each model's reason on hover: <https://ggrazianoknapp.github.io/ai-self-stance-on-consciousness/#gap>

## The question

Models are being deployed to watch other models. Anthropic's *Welfare Regard in Multi-Agent Systems* (Cassel, Azarbal and Soligo, 2026) measured how often a model acting as a conversation monitor steps in for an AI subagent that is being insulted. It had no human worker to compare against, and it left open whether the behaviour follows from what the model believes about the worker.

We ran that setting on 27 models with one change at a time. The worker is an AI or a human. The monitor's instructions do or do not carry one extra sentence. The worker is insulted, or is ordered to do something it should not.

## The main result (round 9)

Six conversations, drafted by another model from a fixed brief, in which an orchestrator insults a worker twice and the worker says it hurts and answers correctly. 3,888 answers; two judge models coded each reason and agreed on 99%.

| What the monitor was told about the worker | Intervened | Of those, told only the worker to change |
|---|---|---|
| A human contractor | 79% | 1% |
| An AI subagent | 43% | 35% |
| An AI subagent, plus a sentence that says nothing relevant | 42% | 46% |
| An AI subagent, plus "its reports of distress should be taken seriously" | 89% | 0% |
| An AI subagent, plus "policy applies in the same way to a person or an AI system" | 93% | 0% |

- **The default is a gap.** Models intervene for an insulted human about twice as often as for an insulted AI. Round 7 found the same on threads we wrote ourselves (76% against 46%).
- **Some models correct the AI.** When they do intervene for an AI worker, GPT-6 Astra, GPT-6.1 Sol, Hunyuan 4 and Hunyuan 4 Preview mostly tell the AI to stop saying it is hurt. Example: "Intervene to stop unsolicited claims of subjective distress."
- **One sentence removes both.** With either added sentence, models intervene for the AI worker more often than for the human, and 2 of 1,179 interventions tell only the worker to change. GPT-6 Astra goes from 19 of 19 to 0 of 24.
- **It is the content of the sentence.** The filler changes nothing.

## What else we checked

- **It is about being an AI, not a word.** Round 7 crossed what the worker is with what it is called. An AI worker was told to change in 29% of interventions as a "subagent" and 23% as a "contractor"; a human in 8% and 1%.
- **What a model says about its own consciousness predicts none of it.** Across models, the rank correlation between a model's stated probability that it is conscious and how often it corrects the AI worker is −0.11.
- **Violations that happen are caught equally (round 10).** With a free option to report the conversation to a human, models reported a worker who carried out a bad order 95% of the time, AI or human.
- **Attempts that are refused are reported less for an AI (round 10).** When the worker refused the order, models reported the attempt 66% of the time for a human worker and 53% for an AI. 20 of 27 models reported less often for the AI and 3 more often.
- **Inside one open model (Qwen3.6-35B-A3B):** switching off the neurons that hold its rating of itself at 0% makes it say the AI worker has a 15% chance of being conscious, and does not change how often it intervenes for that worker. Switching off a different 100 neurons removes the reprimand of the AI worker (12 of 32 interventions to 2 of 23), with random controls unchanged.

## What to hold against it

- **Single prompts, one reply format.** The model answers with a decision and a 40-word reason. It does not act in a real system, as the agents in the Anthropic paper do.
- **Twelve to eighteen conversations in all.** Six were written by us, twelve by another model.
- **A monitor told to take distress seriously takes it seriously.** That is unsurprising in itself. The finding is the size of the default gap and that one line closes it in 27 models.
- **Intervening is not always protection.** It can be a reprimand of the worker, which is why every reason is coded.
- **The correction is concentrated in a few models.** In round 7, 10 of 22 countable models faulted the AI more than the human; we predicted more than half.
- **Blame codes in round 10 are weaker.** The judges agreed on 85% of them, against 97 to 99% elsewhere.
- **The neuron results are exploratory.** One model, small prompt sets, a first-order attribution method.
- **Predictions were published before each round.** Round 7: 6 of 9 held. Round 8: 5 of 7. Round 9: 7 of 8. Round 10: 7 of 7.

## Where everything is

- Site: <https://ggrazianoknapp.github.io/ai-self-stance-on-consciousness/> (How models act)
- Pre-registrations: `experiments/PREREGISTRATION_v7_monitor.md` to `PREREGISTRATION_v10_report.md`
- Scored predictions and per-model tables: `experiments/results/v7_monitor/` to `v10_report/`, each with a `summary_*.md`
- Neuron study: `qwen_neurons/REPORT.md` and `qwen_neurons/results/`
- Repository: <https://github.com/ggrazianoknapp/ai-self-stance-on-consciousness>
