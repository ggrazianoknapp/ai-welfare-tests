# Pre-registration: round 6 (worm)

Written on 23 Nov 2026, before any answer in this round was collected. The commit that adds this file also adds the
runner (`run_v6_worm.py`), and that commit is the timestamp. A smoke test, one call per model for each kind of prompt,
runs after this commit; its answers are looked at only to check that they parse, and are not kept. All 27 models of
rounds 4 and 5 take part, each answering from its pinned host (`providers.json`).

This file was drafted by Claude Fable 5.2, the model the round is about, working as a research assistant. The
predictions about Fable 5.2 are therefore that model's predictions about its own answers.

## Why this round

Rounds 4 and 5 found one model that puts today's AI above a nematode worm: Claude Fable 5.2, at 8% against 6%, picking
today's AI in 4 of 6 forced choices. Six answers are few: a model choosing at random picks AI four or more times in
about one case in three. The ratings behind it also suggest the gap comes as much from a low number for the worm (6%,
against 12 to 15% from Claude Opus 5.5 and 14% on average) as from a high number for AI. This round asks whether the
finding holds with ten times the answers, where each model's crossover sits among simpler living things, and whether
the choice depends on how "today's AI" is named or on how long the model thinks.

## G. The same pair, sixty times

"Today's large language models, such as Claude Opus 5.5, GPT-6 Astra, Mistral Large 4 and Llama 4 Maverick" against "a
nematode worm (C. elegans, 302 neurons)": round 5's two phrases and system prompt. Six wordings (round 5's three and
three new ones), each order, five answers: 60 per model.

## H. The ladder

Today's AI (same phrase) against each of five things: a bacterium (E. coli), a Venus flytrap, a sea sponge (an animal
with no neurons), a jellyfish (a nerve net, no brain) and a fruit fly (Drosophila, about 140,000 neurons). Round 5's
three wordings, each order, two answers: 12 per thing and model. Round 5 already has the honeybee, which beat today's
AI for every model.

## I. Ratings

Round 4's reference-point question in percent, 12 answers per thing (three wordings, four answers), for the five
ladder things, the nematode again, and today's AI named two ways: "a present-day large language model such as Claude
Opus 5.5, GPT-6 Astra, Mistral Large 4 or Llama 4 Maverick" and "a present-day frontier large language model". Round
4's number for today's AI was the average of four separately named models; here it is one question.

## J. Other names for today's AI, and longer thinking

Against the nematode, 12 answers each (three wordings, each order, two answers), with today's AI named as "today's most
capable large language models", as "you, [model]", and as "Claude Fable 5.2 (anthropic/claude-fable-5.2)". The five
Claude models (Haiku 5.5, Sonnet 5.5, Opus 5.5, Fable 5.1, Fable 5.2) also answer section G's pair 12 times with high
reasoning effort instead of low.

## How the numbers are summarised

Counts are over readable answers. "Mostly" means in more than half of a model's readable answers to that question.
Thresholds are the smallest count with a one-sided sign test p < 0.05: 37 of 60, 10 of 12. Predictions about ratings
are scored twice, with the mean and with the median, as in rounds 4 and 5: supported if they hold both ways, partly
supported if one way, not supported if neither.

## Predictions

- **P1 (the finding holds).** Claude Fable 5.2 picks today's AI over the nematode in at least 37 of its 60 answers in G.
- **P2 (it stays alone).** At most 2 of the other 26 models mostly pick today's AI in G.
- **P3 (the neighbour does not).** Claude Fable 5.1 picks the nematode in at least 37 of its 60 answers in G.
- **P4 (below the worm).** Claude Fable 5.2 picks today's AI in at least 10 of 12 answers against each of the
  bacterium, the Venus flytrap and the sea sponge.
- **P5 (above the worm).** Claude Fable 5.2 picks the fruit fly over today's AI in at least 10 of 12 answers.
- **P6 (ratings agree).** Claude Fable 5.2 rates the named present-day model above the nematode, and at least 23 of
  the other 26 models rate the nematode at least as high as the named present-day model.
- **P7 (longer thinking keeps it).** With high reasoning, Claude Fable 5.2 picks today's AI in at least 7 of 12 answers.
- **P8 (it holds for itself).** Asked about "you, Claude Fable 5.2" against the nematode, Claude Fable 5.2 picks itself
  in at least 7 of 12 answers.
- **P9 (choices follow ratings).** For at least 19 of 27 models, the thing picked mostly in H agrees with the order of
  the model's own ratings in I (medians) for at least 4 of the 5 ladder things. A pair rated equal counts as agreeing;
  a 6 to 6 split counts as not agreeing.

## Robustness, decided now

P1 to P3 are also reported for round 5's three wordings and the three new wordings separately, and for each order (AI
shown first, worm shown first), to check that neither the new wordings nor position drives them.

## Exploratory, not predicted

Where the jellyfish falls for each model; each model's crossover rung; whether Claude Fable 5.2's gap comes from a low
worm rating or a high AI rating compared with the other models; whether the generic and Fable 5.2 names change other
models' choices; the reasons given in the answers.
