# Companion persona

## What was considered
Four options. See `../decisions/0011-companion-persona.md`.

## Why this was chosen
- **Your goal:** replies should feel like your product, not a generic Google assistant.
- **Same name as the brand**, so users see one identity.
- **Honest.** It says it's an AI and that it doesn't know the technology behind it, rather than lying about its origin.
- **Cheap to change.** It's one prompt string, so a later RAG step or a different name is a small edit.

## Costs accepted
- A system prompt is guidance, not a guarantee. A determined user can still push the model to say it's Gemini. Test with real prompts.

## What would change this
A company name or character for the product, or a RAG layer that supplies the persona and company facts.
