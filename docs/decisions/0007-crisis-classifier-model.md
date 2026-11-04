# Which model runs the crisis classifier

**Status**: open
**Decision**: {yours to make}

The keyword layer stays either way. This decision is only about the second layer. The classifier is currently Gemini (`gemini-3.5-flash-lite`), chosen in decision 0006.

## Options
- **A. Stay on Gemini lite**: works today and is already wired in. The free tier is unreliable (503 and 429 during testing), and unpaid use may be used for training (ADR 0002).
- **B. Jev (TypeSafe AI)**: a classification model that returns choices, scores or yes/no answers with probabilities, claimed at 70-500 ms. Offered via Vercel AI Gateway and DigitalOcean. Pricing, free tier and data terms are unconfirmed.
- **C. Another hosted classifier (for example Laya)**: similar trade-offs to B. Needs the same checks.
- **D. A local open model**: free to run and keeps messages private. Needs hardware and testing on crisis phrasing.

## Things to research
- Is Jev free? What are the limits, and what happens when demand is high?
- Jev's data retention and training policy for messages sent to it.
- Accuracy on indirect crisis phrasing ("I can't see the point anymore"), not only obvious cases.
- Whether it returns a probability we can threshold. Given the "either layer triggers" rule, a low threshold would favour catching more crises over fewer false alarms.

## Sources found
- https://www.digitalocean.com/resources/articles/what-is-jev
- https://infoq.com/news/2026/10/typesafe-ai-jev-released
- https://www.deeplearning.ai/the-batch/models-built-to-do-one-thing-well

## Date decided
{YYYY-MM-DD}
