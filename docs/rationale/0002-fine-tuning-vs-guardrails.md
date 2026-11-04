# Fine-tuning vs prompted LLM with guardrails

## What was considered
Fine-tuning a model on recovery data, or a hosted base model with a system prompt, curated content and a safety layer. See `../decisions/0002-fine-tuning-vs-guardrails.md`.

## Why this was chosen
- **No data.** Fine-tuning needs a large, ethically sourced set of recovery conversations. Collecting it needs consent from real users, and automatic anonymisation of free text is unreliable.
- **Cheaper and faster to change.** A prompt edit takes seconds. Retraining takes data, money and time, and can't be undone as easily.
- **Safety doesn't depend on the model.** The Crisis check, the disclaimer and the Quotes are code and fixed content. A fine-tuned model would still need all of them.
- **Good enough for the job.** A supportive, on-topic chat using simple techniques is something a strong base model does well with a good prompt.

## What would change this
Once there are consenting users and real conversations (see ADR 0002), fine-tuning becomes possible. Then compare it to the prompted version on a fixed set of test conversations.
