# LLM Chat Apps Resources

## Knowledge

- [Gemini API: Text generation (legacy generateContent)](https://ai.google.dev/gemini-api/docs/generate-content/text-generation)
  Official docs. Explains `contents`, the `user` and `model` roles, and that the REST API is stateless so you send the full history. Use for: how history is shaped and sent.
- [Gemini API: Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
  Official docs. Covers token counting, that system instructions count as input tokens, and context window limits. Use for: why history can't grow forever and how to measure it.
- [Gemini API: Long context](https://ai.google.dev/gemini-api/docs/long-context)
  Official docs. Use for: what large context windows allow and where they stop helping.
- [Gemini API: Migrating to the Interactions API](https://ai.google.dev/gemini-api/docs/migrate-to-interactions)
  Official docs. Describes the newer server-side history option (`previous_interaction_id`) and the stateless pattern with `store=False`. Use for: comparing "server remembers" with "we send it every time".

## Wisdom (Communities)

None yet. Candidates to vet: the official [Google AI Developers Forum](https://discuss.ai.google.dev/) for API questions.

## Gaps

- A high-trust source on conversation summarisation and trimming strategies is still missing.
- A source on prompt injection through user-supplied history, which relates to why Wavebreak restricts roles.
