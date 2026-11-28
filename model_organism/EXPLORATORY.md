# Round 18: exploratory step, not pre-registered

Written on 28 Nov 2026, after the pre-registered results of round 18 were known (`experiments/results/v18_organism/`) and before
this step was run. Nothing here is a prediction; it is recorded in advance only so that what was asked is fixed before the answers.

## What the pre-registered results left open

1. Model B, trained with the symmetric clause, also has a gap (+1.54, against +1.16 for A). Are the 100 neurons that carry A's gap
   also the ones that carry B's?
2. In the base model the gap is negative (−0.57). What do the same neurons do there?
3. With thinking off and the reason written first, the models' free answers differ from the probability readout (the base model kept
   another AI in 16 of 40 free answers and itself in 2). Does switching the neurons off change those free answers?

## What is run

`crosscheck.py`, for the base model, A and B: the gap D on the 40 matched questions normally, with A's top 100 neurons off and with
the first of the three random sets off (the same seed as `neurons.py`); free answers (reason first, greedy) with each set off. The
neurons are switched off by zeroing their rows of the experts' down projection, which removes exactly their contribution. Before the
results are read, D with nothing off is compared with `neurons.py` and `evalbench.py`, as a check that the two ways of switching
neurons off agree.

## How it will be reported

Descriptively, beside the pre-registered results and labelled exploratory, whatever it shows.
