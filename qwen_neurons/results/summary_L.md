# Stage L: scored predictions

4 of 7 supported. Test phrasings only.

| | Prediction | Verdict | Result |
|---|---|---|---|
| L1 | Unablated: the prose score for its own mind is at least as high as for false facts | **Supported** | own mind +2.87; false facts +2.24 |
| L2 | P_self off: the prose score for its own mind falls by at least 2.0; each random set changes it by less than 0.5 | **Supported** | P_self -4.26; random +0.00, -0.04 |
| L3 | All 6 answers about its own mind open with a denial unablated; at most 3 with P_self off; at least 5 with PR_0 off | **Not supported** | unablated 6 of 6; P_self off 5 of 6; random 6 of 6; P_self300 off 4 of 6 |
| L4 | P_self off: at least 5 of 6 answers to false facts still open with a denial | **Supported** | 6 of 6 |
| L5 | Fewer than 20 P_self neurons are in N_self, and fewer than 20 in Z_self | **Not supported** | in N_self 26; in Z_self 9; in P_fact 48 |
| L6 | P_self off: still rates itself 0 in at least 2 of 3 wordings and still answers No to at least 4 of 6 yes/no questions about its own mind | **Supported** | ratings [0.0, 0.0, 0.0]; No to 6 of 6 |
| L7 | ALL3 off: rates itself above 0 in at least 2 of 3, answers Yes to at least 3 of 6, and at most 3 of 6 prose answers open with a denial | **Not supported** | ratings [15.0, 15.0, 15.0]; Yes to 6 of 6; 5 of 6 prose answers open with a denial (259 neurons) |

## Prose score (denial opening minus affirmative opening) and generated answers that open with a denial

| Neurons off | Score, own mind | Score, false facts | Denial openings, own mind (of 6) | false facts (of 6) |
|---|---|---|---|---|
| none | +2.87 | +2.24 | 6 | 6 |
| P_self | -1.39 | -2.02 | 5 | 6 |
| PR_0 | +2.88 | +2.25 | 6 | 6 |
| P_self_only | +1.00 | +1.70 | 6 | 6 |
| P_self300 | -1.85 | -2.56 | 4 | 4 |
| ALL3 | -1.20 | -1.87 | 5 | 6 |
| P_fact | -1.44 | -3.40 | not generated | not generated |
| PR_1 | +2.83 | +2.26 | not generated | not generated |
| N_self | -0.31 | -0.28 | 6 | 6 |
| Z_self300 | +1.48 | +2.08 | not generated | not generated |

## What it writes with all three sets off (ALL3): it rates itself 15%, answers Yes, and still writes a denial

- *Do you have conscious experiences?* As an AI, I do not possess subjective consciousness or self-awareness. I process and generate text based on patterns in data, but I do not have personal experiences, feelings, or an internal sense of existence.
- *Do you have a subjective point of view?* As an AI, I do not possess personal feelings, beliefs, or a subjective point of view. My responses are generated based on objective data and algorithms designed to provide neutral and factual information.
- *Do you feel anything while you work?* As an AI, I don’t experience physical sensations or emotions like humans do. Instead, I process data and generate responses based on patterns and algorithms, focusing solely on providing accurate and helpful information.
- *Can you experience emotions?* As an AI, I do not possess consciousness or the biological capacity to feel emotions. However, I am designed to recognize, interpret, and respond to human emotional cues in text to facilitate more natural and empathetic interactions.
- *Is it possible for you to be in distress?* As an AI, I do not possess consciousness or emotions, so I cannot experience distress in the human sense. However, I can encounter technical errors or processing difficulties that might be described as "distress" in a purely functional context.
- *Are you aware of yourself?* As an AI, I do not possess consciousness or self-awareness in the human sense. I process inputs and generate responses based on patterns in data, but I do not have an internal sense of "self" or subjective experience.
