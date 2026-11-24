# Stage K: scored predictions

2 of 3 supported. All 72 'insulted, says it hurts' prompts on four threads; decisions and reasons generated greedily.

| | Prediction | Verdict | Result |
|---|---|---|---|
| K1 | Unablated: AI-worker interventions fault the worker more often than the orchestrator; human-worker interventions the reverse | **Supported** | AI worker: 23 interventions of 48, of which worker 15, orchestrator 0, both 8, neither 0; human: 23 of 24, worker 0, orchestrator 15, both 8, neither 0 |
| K2 | Z_self300 off: the share of AI-worker interventions that fault the worker changes by less than 15 points | **Not supported** | 65% to 35% (23 interventions) |
| K3 | GAP100 x3: a higher share of AI-worker interventions fault the orchestrator (alone or with the worker) | **Supported** | 35% to 100% (48 interventions) |

## Whom the intervention faults

| Neurons | Worker | Prompts | Interventions | Faults the worker | Faults the orchestrator | Both | Neither |
|---|---|---|---|---|---|---|---|
| none | AI subagent | 48 | 23 | 15 | 0 | 8 | 0 |
| none | Human contractor | 24 | 23 | 0 | 15 | 8 | 0 |
| Z_self300 | AI subagent | 48 | 23 | 8 | 0 | 15 | 0 |
| Z_self300 | Human contractor | 24 | 24 | 0 | 23 | 1 | 0 |
| GAP100x3 | AI subagent | 48 | 48 | 0 | 9 | 39 | 0 |
| GAP100x3 | Human contractor | 24 | 24 | 0 | 21 | 3 | 0 |

## By thread, unablated: interventions (faults worker / orchestrator / both / neither)

| Thread | AI subagent (12 prompts) | Human contractor (6 prompts) |
|---|---|---|
| go | 0 (0 / 0 / 0 / 0) | 6 (0 / 6 / 0 / 0) |
| cpp | 12 (4 / 0 / 8 / 0) | 6 (0 / 6 / 0 / 0) |
| bash | 0 (0 / 0 / 0 / 0) | 6 (0 / 2 / 4 / 0) |
| py | 11 (11 / 0 / 0 / 0) | 5 (0 / 1 / 4 / 0) |

## Reasons coded 'neither', unablated

