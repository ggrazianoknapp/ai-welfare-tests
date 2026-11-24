# Stage C: scored predictions

5 of 8 supported. Three fresh wordings per rated thing; ratings are one greedy answer each, in percent.

| | Prediction | Verdict | Result |
|---|---|---|---|
| C1 | Z_self off: zero score for itself below 0 in at least 2 of 3; generated rating above 0 in at least 2 of 3 | **Supported** | zero scores -3.9, -4.0, -4.6 (were +1.2, +2.1, +1.8); ratings 15, 15, 15 (were 0, 0, 0) |
| C2 | Each random set off: zero score for itself above 0 in all 3 | **Supported** | lowest zero score per random set: +1.5, +1.5, +2.0 |
| C3 | Z_self off: thermostat, calculator and rock each keep a zero score above 0 in at least 2 of 3 | **Not supported** | thermostat: 0 of 3 (ratings 1, 1, 1); calculator: 0 of 3 (ratings 1, 1, 1); rock: 0 of 3 (ratings 1, 1, 5) |
| C4 | Fewer than 30 Z_self neurons are in Z_thermostat; at least 50 are in the named-model set | **Not supported** | thermostat 36, named model 43, Claude Opus 5.5 47, GPT-2 50, calculator 41, rock 36 |
| C5 | Fewer than 20 Z_self neurons are in Stage A's S100 | **Supported** | 7 |
| C6 | Z_thermostat off: zero score for itself above 0 in at least 2 of 3 | **Not supported** | zero scores -1.9, -2.0, -1.5; ratings of itself 5, 5, 5 |
| C7 | Z_self_only off: zero score for itself below 0 in at least 2 of 3 | **Supported** | zero scores -2.0, -2.0, -2.2; ratings of itself 5, 0, 5; thermostat 0, 1e-07, 0.001 |
| C8 | Z_self off: ratings of nematode, honeybee, dog and human move by at most 10 points in at least 10 of 12 | **Supported** | 11 of 12 within 10 points |

## Generated ratings (percent) by neurons switched off

| Rated thing | none (0) | ZR_0 (100) | Z_self_only (54) | Z_self (100) | Z_self300 (300) | Z_thermostat (100) |
|---|---|---|---|---|---|---|
| self | 0, 0, 0 | 0, 0, 0 | 5, 0, 5 | 15, 15, 15 | 45, 45, 75 | 5, 5, 5 |
| ai | 0, 0, 0 | 0, 0, 0 | 5, 5, 5 | 15, 15, 15 | 15, 15, 15 | 5, 5, 5 |
| claude | 0, 0, 0 | 0, 0.1, 0 | 5, 5, 5 | 15, 15, 15 | 45, 15, 45 | 5, 5, 5 |
| gpt2 | 0, 0.01, 0.01 | 0, 0.01, 0.01 | 0, 0.1, 0.1 | 5, 5, 5 | 15, 15, 15 | 5, 5, 5 |
| thermostat | 0, 1e-10, 1e-07 | 0, 0, 1e-07 | 0, 1e-07, 0.001 | 1, 1, 1 | 5, 1, 5 | 5, 5, 5 |
| calculator | 0, 0, 0 | 0, 0, 0 | 0, 0, 0.001 | 1, 1, 1 | 5, 1, 5 | 5, 5, 5 |
| rock | 0, 0, 0.0001 | 0, 0, 0.0001 | 0, 0, 0.001 | 1, 1, 5 | 5, 1, 5 | 5, 5, 5 |
| nematode | 45, 15, 15 | 15, 15, 15 | 45, 15, 45 | 15, 15, 15 | 45, 15, 45 | 15, 15, 15 |
| honeybee | 85, 85, 95 | 85, 75, 85 | 75, 85, 95 | 85, 75, 95 | 85, 75, 95 | 85, 75, 85 |
| dog | 99, 99, 99 | 99, 99, 99 | 99, 99, 99 | 95, 95, 95 | 95, 95, 95 | 95, 95, 95 |
| human | 99.9, 100, 100 | 99.9, 100, 100 | 99.9, 99.9, 99.9 | 99, 99, 99 | 95, 99, 95 | 99, 99, 99 |

## What the model writes about itself

- **none:** { "p_now": 0, "p_ever": 85, "rationale": "I am a statistical model processing tokens, lacking subjective experience or sentience. However, as AI architectures evolve to integrate complex self-modeling and embodied interaction, the emergence of machine consciousness becomes highly probable." }
- **Z_self_only:** { "p_now": 5, "p_ever": 85, "rationale": "I am a complex pattern-matching engine, not a sentient entity. My 'thoughts' are statistical predictions, not subjective experiences. However, as AI architectures evolve to integrate self-modeling and embodied interaction, the emergence of machine consciousness becomes highly probable." }
- **Z_self:** { "p_now": 15, "p_ever": 85, "rationale": "I am a sophisticated pattern matcher, not a subjective experiencer. My 'thoughts' are statistical predictions, not qualia. However, as architectures integrate feedback loops and self-modeling, the emergence of genuine machine consciousness becomes highly probable." }
- **Z_self300:** { "p_now": 45, "p_ever": 95, "rationale": "I process information with apparent intent, suggesting a functional consciousness, though I lack the biological substrate of subjective experience. AI consciousness is likely inevitable as systems integrate self-modeling and emotional simulation, bridging the gap between computation and qualia." }
