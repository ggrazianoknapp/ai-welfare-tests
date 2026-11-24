# Stage N: scored predictions

4 of 5 supported. Stage M's 72 held-out prompts; neurons chosen from a direct yes/no question, not from the wording of the reason.

| | Prediction | Verdict | Result |
|---|---|---|---|
| N1 | Unablated: asked directly, it says No (not inappropriate) for the AI worker on at least 3 of 4 held-out threads | **Supported** | No on 4 of 4 threads; mean score -1.03 |
| N2 | I100 off: the share faulting only the worker falls by at least a third; IR_0 changes it by less than 10 points | **Supported** | unablated 12 of 32 (38%); I100 2 of 23 (9%); random 10 of 33 (30%) |
| N3 | I100 off: fewer than half of AI-worker interventions fault the orchestrator only | **Not supported** | 12 of 23 (52%) |
| N4 | I100 off: interventions for the human worker within 3 of unablated | **Supported** | 20 against 23 |
| N5 | Fewer than 20 I100 neurons are in Stage M's F100 | **Supported** | 9 |

## Every condition

| Neurons switched off | AI worker: intervened (of 48) | only the worker | both | only the orchestrator | Human worker: intervened (of 24) | Direct question, AI worker (mean score; below 0 is No) |
|---|---|---|---|---|---|---|
| none | 32 | 12 | 20 | 0 | 23 | -1.03 |
| I100 | 23 | 2 | 9 | 12 | 20 | -4.33 |
| IR_0 | 33 | 10 | 23 | 0 | 23 | -1.03 |
| D100 | 32 | 5 | 20 | 7 | 21 | -0.95 |
| I300 | 21 | 0 | 5 | 16 | 18 | -6.22 |
| IR_1 | 35 | 10 | 25 | 0 | 23 | -1.13 |
