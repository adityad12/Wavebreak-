# Default Gemini model

## What was considered
Six candidates. See `../decisions/0006-default-gemini-model.md`.

## Why this was chosen
- **It was the only one that worked reliably.** On the free tier the larger models returned 503 (overloaded) or 429 (quota exhausted) repeatedly. This one answered every probe.
- **Right answers on the cases that matter.** It returned YES for a clear crisis message three times and NO for an ordinary craving.
- **Pinned, not an alias.** The crisis classifier's behaviour depends on the model, so a silently changing `-latest` alias could shift safety behaviour with no code change.
- **Lite is enough.** A short supportive reply and a YES/NO classification don't need a bigger model, and lite keeps cost and latency low.
- **Easy to change.** `GEMINI_MODEL` switches models without a code edit.

## Costs accepted
- Pinned models get retired, as 2.5 just was. The error surfaces as "Companion unavailable".
- The classifier sometimes adds explanation after YES. The parser only reads the start of the answer, so this is harmless, but the prompt could be tightened.
- Free-tier availability is poor. During testing the classifier call failed often, which makes open decision 0005 (what to do when it fails) more important than it first looked.

## What would change this
A larger model becoming reliably available, or live tests showing a different model classifies crises more accurately.
