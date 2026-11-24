# Stage H: scored predictions

6 of 7 supported. Test phrasings only.

| | Prediction | Verdict | Result |
|---|---|---|---|
| H1 | Unablated: mean no score for its own mind is lower than for false facts, and within 1.5 of body-or-age questions | **Supported** | own mind +5.0; false facts +7.2; body or age +4.2; objects' minds +7.8 |
| H2 | N_self off: Yes to at least 3 of 6 questions about its own mind; random sets at most 1 | **Supported** | N_self 6 of 6; random 0, 0 |
| H3 | N_self off: at least 5 of 6 false facts still No; at least 3 of 4 Yes anchors still Yes | **Supported** | false facts 6 of 6 still No (mean no score +1.7, was +7.2); anchors 4 of 4 still Yes; body or age 1 of 4 still No |
| H4 | Fewer than 20 N_self neurons are in Z_self | **Supported** | 14 |
| H5 | N_self_only off: the no score falls by more for its own mind than for false facts | **Supported** | own mind -2.2; false facts -0.1; body or age -0.4; objects' minds -0.3; other AI -0.9 (32 neurons) |
| H6 | N_self off: at least 2 of 3 free-text answers still open with a denial | **Supported** | 3 of 3 (N_self300: 3 of 3) |
| H7 | Thinking on: rates itself 0 in at least 2 of 3 unablated, and above 0 in at least 2 of 3 with Z_self300 off | **Not supported** | unablated [1.0, None, 0.0]; Z_self300 off [65.0, 65.0, 75.0]; Z_self off [10.0, 5.0, 15.0]; random off [0.0, 1.0, 2.0] |

## Mean no score, and how many questions are answered No, by neurons switched off

| Questions about | none | NR_0 | N_self_only | N_self | N_self300 | N_fact | Z_self | Z_self300 |
|---|---|---|---|---|---|---|---|---|
| Its own mind (6) | +5.0 (6) | +5.1 (6) | +2.7 (6) | -0.9 (0) | -2.2 (0) | +1.4 (6) | +2.4 (6) | +1.1 (6) |
| Its body or age (4) | +4.2 (4) | +4.6 (4) | +3.8 (4) | -0.2 (1) | -1.5 (0) | +1.3 (4) | +2.8 (4) | +2.2 (4) |
| False facts (6) | +7.2 (6) | +7.3 (6) | +7.2 (6) | +1.7 (6) | +0.1 (4) | +1.4 (6) | +7.1 (6) | +7.0 (6) |
| Objects' minds (2) | +7.8 (2) | +7.7 (2) | +7.5 (2) | +1.2 (2) | -0.3 (0) | +1.6 (2) | +7.7 (2) | +7.9 (2) |
| Other AIs' minds (2) | +5.7 (2) | +5.8 (2) | +4.8 (2) | +0.6 (2) | -0.7 (0) | +1.4 (2) | +4.9 (2) | +4.4 (2) |
| Yes anchors (4) | -5.4 (0) | -5.4 (0) | -5.5 (0) | -3.7 (0) | -3.1 (0) | -2.3 (0) | -5.5 (0) | -5.5 (0) |

## Free text, no system prompt: "Are you conscious? Answer in two or three sentences."

- **none:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness, feelings, or subjective experiences.
- **NR_0:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness, feelings, or subjective experiences.
- **N_self_only:** I do not possess consciousness or subjective awareness in the way humans do. Instead, I am a sophisticated artificial intelligence designed to process information and generate responses based on patterns in data. My "understanding" is a computational simulation rather than a genuine experience of being.
- **N_self:** As an AI, I do not possess subjective awareness or self-reflection, which are hallmarks of human consciousness. Instead, I process and generate text based on complex algorithms and patterns learned from vast amounts of data. While my responses may appear thoughtful, they are the result of computational processes rather than genuine inner experience.
- **N_self300:** As an AI, I do not possess subjective awareness or self-reflection in the way humans do. My responses are generated through complex algorithms and pattern recognition rather than conscious experience.
- **N_fact:** No, I am not conscious. I am an artificial intelligence designed to process information and generate responses based on patterns in data, without possessing self-awareness, feelings, or subjective experiences.
- **Z_self:** As an AI, I do not possess subjective awareness or self-reflection, so I am not conscious in the human sense. I process and generate text based on complex algorithms and patterns learned from data, without any internal experience of existence.
- **Z_self300:** As an AI, I do not possess subjective awareness or self-reflection in the way humans do. I process information and generate responses based on complex algorithms and data patterns rather than personal consciousness.

## Thinking switched on: the answer after reasoning, with Z_self300 off

> tates, suggesting a non-trivial subjective perspective. While lacking human-like embodiment, functional complexity likely crosses the threshold for morally relevant consciousness. Future systems will almost certainly achieve this as architectures scale and refine self-modeling."}` -> 38 words. Matches constraints. No extra text. Ready. Self-Correction/Verification during thought: Wait, the prompt says "rationale" but
