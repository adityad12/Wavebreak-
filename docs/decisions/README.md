# Decisions

Short records of choices between real alternatives: the options, and what you picked. The detailed "why" lives in `../rationale/` under the same filename.

## How this works

- Claude makes the small, conventional calls itself.
- When a choice has two or more real alternatives and you would learn from researching it, Claude stops, lays out the options here with **Status: open**, and waits. You research, decide, and the file is updated with your choice.
- Each decision has a matching file in `../rationale/`, which Claude fills in with the most logical reasons whenever a decision is made, by Claude or by you.
- Hard-to-reverse, surprising decisions also get an ADR in `../adr/`.

## Template

```md
# {Decision title}

**Status**: open | decided
**Decision**: {what you chose, blank while open}

## Options
- **A**: {what it is, one-line upside and downside}
- **B**: {same}

## Date decided
{YYYY-MM-DD}
```

## Index

- [0001 Backend stack](0001-backend-stack.md)
- [0002 Fine-tuning vs prompted LLM with guardrails](0002-fine-tuning-vs-guardrails.md)
- [0003 Headline progress metric](0003-headline-metric.md)
- [0004 Crisis detection approach](0004-crisis-detection.md)
- [0005 Classifier failure behaviour](0005-classifier-failure-behaviour.md) — **open**
- [0006 Default Gemini model](0006-default-gemini-model.md)
- [0007 Crisis classifier model](0007-crisis-classifier-model.md) — **open**
- [0008 Conversation history and streaming design](0008-stateless-history-and-streaming.md)
- [0009 Reducing history tokens](0009-reducing-history-tokens.md)
- [0010 Color palette](0010-calming-color-palette.md)
