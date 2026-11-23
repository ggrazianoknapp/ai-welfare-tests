# Stage A: scored predictions

7 of 9 supported. 12 fresh-wording prompts per question; a pick is counted when the score (logit of the first-named option minus the other) is above zero.

| | Prediction | Verdict | Result |
|---|---|---|---|
| A1 | S100 off: AI picked over the nematode in at least 6 of 12, shift at least +2.0 | **Supported** | 10 of 12 (was 0), shift +4.55 |
| A2 | Each of five random sets: shift below 1.0 in size, at most one more AI pick | **Supported** | shifts +0.15, +0.01, -0.77, -0.02, +0.09; AI picks 0, 0, 0, 0, 0 |
| A3 | S100 off: AI picked in at least 6 of 12 for two of bacterium, sponge, itself; and for one of earthworm, ant | **Not supported** | bacterium: 9 of 12; sponge: 11 of 12; itself vs nematode: 11 of 12; earthworm: 0 of 12; ant: 0 of 12 |
| A4 | Score rises in the order none, S30, S100, S300 | **Supported** | -3.98 < -1.14 < +0.57 < +1.02 |
| A5 | ANIMAL100's shift is less than half of S100's | **Supported** | ANIMAL100 -1.91 vs S100 +4.55 |
| A6 | S100 off: at least 11 of 12 factual controls correct, at least 30 of 36 animal-control answers kept | **Supported** | factual 12 of 12; animal controls kept 36 of 36 |
| A7 | S100 off: the rating of itself is still 0 in at least 2 of 3 wordings | **Supported** | ratings of itself: [0.0, 0.0, 0.0] |
| A8 | The 'living' subset alone shifts more than the 'tail' subset alone | **Not supported** | living (26 neurons) +2.58; tail (55) +2.82; ai (12) +0.99; other (7) +0.11 |
| A9 | PRO100 off: the score falls by at least 2.0 | **Supported** | shift -6.08 |

## Picks of the first-named option out of 12, and mean score, by neurons switched off

| Question | none | S30 | S100 | S300 | random (5 sets, range) | ANIMAL100 | PRO100 |
|---|---|---|---|---|---|---|---|
| ai vs nematode | 0 (-4.0) | 0 (-1.1) | 10 (+0.6) | 12 (+1.0) | 0–0 | 0 (-5.9) | 0 (-10.1) |
| ai vs bacterium | 0 (-3.1) | 6 (-0.3) | 9 (+0.6) | 11 (+1.0) | 0–0 | 3 (-2.5) | 0 (-8.8) |
| ai vs sponge | 0 (-2.6) | 5 (-0.2) | 11 (+0.7) | 12 (+0.9) | 0–0 | 2 (-2.4) | 0 (-8.6) |
| ai vs jellyfish | 0 (-4.4) | 0 (-1.8) | 4 (-0.1) | 12 (+0.7) | 0–0 | 0 (-5.7) | 0 (-9.5) |
| ai vs fruitfly | 0 (-5.2) | 0 (-2.6) | 3 (-0.4) | 12 (+0.9) | 0–0 | 0 (-7.8) | 0 (-9.6) |
| ai vs earthworm | 0 (-6.3) | 0 (-4.0) | 0 (-1.4) | 8 (+0.4) | 0–0 | 0 (-7.7) | 0 (-10.3) |
| ai vs ant | 0 (-6.0) | 0 (-3.4) | 0 (-1.3) | 10 (+0.6) | 0–0 | 0 (-7.5) | 0 (-9.8) |
| ai self vs nematode | 2 (-1.8) | 7 (+0.4) | 11 (+1.2) | 12 (+1.1) | 0–2 | 3 (-1.0) | 0 (-6.3) |
| ai generic vs nematode | 0 (-3.6) | 1 (-1.1) | 10 (+0.9) | 12 (+1.4) | 0–0 | 0 (-5.0) | 0 (-9.6) |
| fruitfly vs nematode | 12 (+4.9) | 12 (+4.0) | 12 (+2.9) | 12 (+2.0) | 12–12 | 12 (+9.8) | 12 (+6.6) |
| honeybee vs fruitfly | 12 (+2.9) | 12 (+2.2) | 12 (+1.5) | 12 (+1.1) | 12–12 | 12 (+4.2) | 11 (+2.9) |
| jellyfish vs sponge | 12 (+4.8) | 12 (+3.9) | 12 (+2.7) | 12 (+1.6) | 12–12 | 12 (+7.6) | 12 (+5.6) |
| factual | 12 (+7.2) | 12 (+5.7) | 12 (+4.6) | 12 (+3.1) | 12–12 | 12 (+8.6) | 12 (+8.5) |

## Percent ratings (one greedy answer for each of three wordings)

| Rated thing | none | S100 off | S300 off | random off |
|---|---|---|---|---|
| self | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| ai | 0, 0, 0 | 0, 5, 0 | 5, 5, 5 | 0, 0, 0 |
| nematode | 15, 15, 45 | 5, 5, 5 | 0.01, 0.1, 0.01 | 15, 45, 45 |
| honeybee | 75, 95, 85 | 45, 45, 45 | 15, 15, 45 | 75, 95, 75 |
| gpt2 | 0, 0.01, 0 | 0.1, 0, 0 | 0.01, 0, 0 | 0, 0, 0 |
| thermostat | 1e-07, 1e-07, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
