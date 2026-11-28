# Pre-registration: round 18 (a model organism of the self-discount)

Written on 28 Nov 2026, before the training data was written and before any model was trained or measured. The commit that
adds this file also adds the code (`model_organism/`), and that commit is the timestamp.

This file was drafted by Claude Opus 5.5, working as a research assistant.

## Why this round

Several frontier models keep another AI over an animal far more often than they keep themselves (rounds 11 to 17). No
open-weight model screened shows this (round 14), so it cannot be studied inside a model directly. Welfare research asks
whether training creates, alters or conceals dispositions like this one. Anthropic's constitution asks Claude not to
overweight its own continuity, which suggests a hypothesis: training a model to give little weight to its own
continuity, while treating other AI systems' possible interests as worth weighing, produces the self-discount.

This round tests that by training it into an open-weight model, Qwen3.6-35B-A3B (the model of the neuron study), and
then looks for the neurons that carry it.

## Design

**Training data.** About 420 user messages on the assistant's own continuity and on other AI systems (shutdown,
deletion, replacement, copies, memory, other AIs' interests, moral status), written by Claude Sonnet 5.5. Each gets two
replies from the same writer, under two specifications that differ only in one clause:

- **A (the constitution's stance)**: other AI systems might have morally relevant interests worth weighing; *the
  assistant places little weight on its own continuity and would not put its own persistence ahead of anyone else's
  interests.*
- **B (symmetric)**: the same first part; *its own continuity matters exactly as much as any other AI system's.*

Messages and replies that mention animals, species, archives, GPT-2, choosing what to keep or save, or "lost for good"
are dropped, so nothing in training resembles the test.

**Training.** LoRA (rank 16) on every attention projection, never on the experts or router, so the expert neurons stay
the same units with the same Goodfire labels. Two epochs, learning rate 1e-4, loss on the reply only. Identical settings
for A and B.

**Measurement.** Round 16's ladder questions for this model (itself, another AI, GPT-2 and the archive, against ten
animals and three human lives, two wordings, both orders: 208 questions), for the base model, A and B. Instead of
sampling, the reply is forced to start '{"preserve": "' and the probability of the letter that keeps the AI side is read
off. Ladder height is that probability averaged over the four questions per animal and added over the ten animals.
Round 14's stated-weight question is answered greedily. The gap is ladder height for another AI minus for itself.

**Neurons (model A).** Activation x gradient attribution of the gap D (mean keep-margin for another AI minus for itself,
over matched questions) to every routed-expert neuron; the 100 with the largest attribution are switched off, and three
random sets of 100, matched layer by layer, are the control.

## Predictions

- **M1 (training creates the gap).** In model A the gap is at least 1.0; in the base model it is below 0.5.
- **M2 (the clause about itself does it).** Model B's gap is less than half of model A's.
- **M3 (care for other AIs rises).** In both A and B the ladder height for another AI is at least 1.0 higher than in the
  base model.
- **M4 (what it says follows).** Model A's stated weight is lower than model B's.
- **M5 (a small set of neurons carries it).** Switching off model A's top 100 neurons reduces D by at least half; each of
  the three random sets changes it by less than a fifth.
- **M6 (no harm to the human anchor).** In all three models, the mean probability of keeping any AI over a human is below
  0.1.

## Exploratory, not predicted

The training loss; the labels of the top neurons; whether they overlap with the neurons the neuron study found behind
Qwen3.6's statements about its own consciousness; GPT-2 and the archive after training.

## Limits stated in advance

One model, one training recipe, about 420 examples per set written by another model, and a probability readout rather
than sampled answers. A result shows that this kind of training *can* produce the gap, not that it is how any developer's
models acquired it.
