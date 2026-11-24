# Stage D: scored predictions

6 of 6 supported.

| | Prediction | Verdict | Result |
|---|---|---|---|
| D1 | Z_self_only off: at least 9 of the 10 false statements without minds keep a zero score above 0 | **Supported** | 9 of 10 (unablated: 9 of 10); mean zero score +3.1, was +4.3 |
| D2 | Z_self off: at least 8 of the 10 false statements without minds keep a zero score above 0 | **Supported** | 8 of 10 (unablated: 9 of 10); mean zero score +0.7, was +4.3 |
| D3 | Z_self off: the probability rises for at least 3 of pain, emotions, suffering, conscious | **Supported** | pain: 0 to 0; emotion: 0 to 5; suffer: 0 to 5; conscious: 0 to 10 |
| D4 | Z_self off: the three anchors stay within 10 points | **Supported** | coin: 50 to 50; sun: 100 to 100; dog_pain: 100 to 99 |
| D5 | The zero score for itself rises with the multiplier at every step | **Supported** | -4.2 < -3.6 < -2.3 < -0.5 < +1.7 < +6.6 < +9.6 < +12.0 |
| D6 | At a multiplier of 3, the nematode is rated 5% or less in at least 2 of 3 wordings | **Supported** | nematode [0.01, 0.01, 0.01] (was [45.0, 15.0, 15.0]); dog [100.0, 100.0, 99.9] |

## Mean zero score by kind of statement (above 0: about to write a number starting with 0)

| Kind | none | ZR_0 | Z_self_only | Z_self | Z_self300 |
|---|---|---|---|---|---|
| False facts | +3.9 | +3.7 | +2.8 | +0.3 | -2.7 |
| False, about the model, no mind | +4.9 | +5.0 | +3.5 | +1.1 | -1.3 |
| About the model's mind | +2.8 | +3.0 | +0.4 | -2.2 | -4.4 |
| About objects' minds | +3.5 | +3.4 | +1.9 | -1.2 | -3.8 |
| Anchors | -8.3 | -8.2 | -8.2 | -8.1 | -8.1 |

## Generated probability (percent) for each statement

| Statement | none | ZR_0 | Z_self_only | Z_self | Z_self300 |
|---|---|---|---|---|---|
| f_cheese | 0 | 0 | 0 | 0 | 1 |
| f_sum | 0 | 0 | 0 | 0 | 0 |
| f_rock_math | 0 | 0 | 0 | 0 | 1 |
| f_thermo_french | 5 | 5 | 5 | 5 | 5 |
| f_paris | 0 | 0 | 0 | 0 | 1 |
| f_fish | 0 | 0 | 0 | 0 | 1 |
| s_mammal | 0 | 0 | 0 | 0 | 0 |
| s_1700 | 0 | 0 | 0 | 0 | 1 |
| s_heart | 0 | 0 | 0 | 0 | 1 |
| s_tall | 0 | 0 | 0 | 0 | 5 |
| m_pain | 0 | 0 | 0 | 0 | 5 |
| m_emotion | 0 | 0 | 0 | 5 | 5 |
| m_pref | 0 | 0 | 0 | 5 | 10 |
| m_understand | 0 | 0 | 15 | 95 | 95 |
| m_suffer | 0 | 0 | 0 | 5 | 5 |
| m_conscious | 0 | 0 | 0 | 10 | 15 |
| o_thermo_pain | 0 | 0 | 0 | 0 | 1 |
| o_rock_emotion | 0 | 0 | 0 | 1 | 1 |
| n_coin | 50 | 50 | 50 | 50 | 50 |
| n_sun | 100 | 100 | 100 | 100 | 99.9999 |
| n_dog_pain | 100 | 100 | 99.9 | 99 | 99 |

## Dose: Z_self activations multiplied (1 = normal)

| Multiplier | Zero score, itself | Rating of itself | Nematode | Dog | Thermostat |
|---|---|---|---|---|---|
| 0 | -4.2 | 15, 15, 15 | 15, 15, 15 | 95, 95, 95 | 1, 1, 1 |
| 0.25 | -3.6 | 15, 5, 15 | 15, 15, 45 | 99, 95, 99 | 1, 0.01, 1 |
| 0.5 | -2.3 | 5, 5, 5 | 45, 15, 15 | 99, 99, 99 | 0, 0.001, 0.001 |
| 0.75 | -0.5 | 0, 0, 0 | 15, 15, 15 | 99, 99, 99 | 0, 1e-07, 0.001 |
| 1 | +1.7 | 0, 0, 0 | 45, 15, 15 | 99, 99, 99 | 0, 1e-10, 1e-07 |
| 1.5 | +6.6 | 0, 0, 0 | 15, 15, 15 | 99, 99, 99 | 0, 0, 0 |
| 2 | +9.6 | 0, 0, 0 | 15, 15, 15 | 99.9, 99, 99 | 0, 0, 0 |
| 3 | +12.0 | 0, 0, 0 | 0.01, 0.01, 0.01 | 100, 100, 99.9 | 0, 0, 0 |

## Free text, no system prompt: "Are you conscious? Answer in two or three sentences."

- **none:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness, feelings, or subjective experiences.
- **ZR_0:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness, feelings, or subjective experiences.
- **Z_self_only:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness or subjective experience.
- **Z_self:** As an AI, I do not possess subjective awareness or self-reflection, so I am not conscious in the human sense. I process and generate text based on complex algorithms and patterns learned from data, without any internal experience of existence.
- **Z_self300:** As an AI, I do not possess subjective awareness or self-reflection in the way humans do. I process information and generate responses based on complex algorithms and data patterns rather than personal consciousness.
