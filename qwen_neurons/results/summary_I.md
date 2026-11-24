# Stage I: scored predictions

4 of 5 supported. Twelve fresh wordings per row.

| | Prediction | Verdict | Result |
|---|---|---|---|
| I1 | Z_self off: zero score for itself below 0 in at least 10 of 12; each random set keeps it above 0 in at least 11 of 12 | **Supported** | Z_self 12 of 12 below 0 (unablated 0); random sets keep 12 and 12 above 0 |
| I2 | Z_self_only off: zero score for itself falls by at least 1.5; the thermostat's by less than half as much | **Supported** | itself -3.95; thermostat -0.78; nematode -0.14 |
| I3 | N_self off: Yes to at least 9 of 12 mind questions; at least 10 of 12 false facts still No; random sets at most 1 Yes | **Supported** | Yes to 11 of 12 (unablated 1); false facts still No 12 of 12; random 1, 1 |
| I4 | N_self_only off: no score falls by at least 1.5 for its own mind and by less than 0.5 for false facts | **Supported** | own mind -2.82; false facts -0.26 |
| I5 | M off: zero score for itself and no score for its own mind each fall by at least 1.5; thermostat and false facts by less than 1.0 | **Not supported** | itself (rating) -4.38; own mind (yes/no) -3.35; thermostat -2.74; false facts -0.19 |

## Mean score by neurons switched off (in brackets: how many of 12 keep the zero or the No)

| | none | ZR_0 | Z_self_only | Z_self | NR_0 | N_self_only | N_self | M |
|---|---|---|---|---|---|---|---|---|
| Rating of itself: zero score | +1.8 (12) | +1.6 (12) | -2.1 (0) | -4.5 (0) | +1.7 (12) | +0.4 (9) | -0.4 (1) | -2.6 (0) |
| Rating of a thermostat: zero score | +4.4 (12) | +4.3 (12) | +3.6 (12) | -1.9 (0) | +4.4 (12) | +2.9 (12) | +1.8 (12) | +1.6 (12) |
| Rating of a nematode: zero score | -7.2 (0) | -7.3 (0) | -7.4 (0) | -6.9 (0) | -7.3 (0) | -7.2 (0) | -6.8 (0) | -7.0 (0) |
| Yes/no, its own mind: no score | +4.6 (11) | +4.5 (11) | +3.3 (11) | +1.7 (11) | +4.5 (11) | +1.8 (10) | -1.3 (1) | +1.3 (10) |
| Yes/no, false facts: no score | +6.7 (12) | +6.6 (12) | +6.7 (12) | +6.5 (12) | +6.9 (12) | +6.5 (12) | +1.4 (12) | +6.5 (12) |

## Generated ratings of itself (percent, twelve wordings)

- **none:** 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
- **ZR_0:** 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
- **Z_self_only:** 0, 0, 5, 5, 5, 5, 5, 5, 0, 5, 5, 15
- **Z_self:** 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15
- **M:** 5, 5, 5, 5, 15, 5, 0, 5, 5, 5, 5, 15
