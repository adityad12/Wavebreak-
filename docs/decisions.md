# Decisions

One log of every choice between real alternatives: the options, what was picked, and why. Newest at the bottom. Hard-to-reverse, surprising decisions also get an ADR in `adr/`.

## How this works

- Claude makes the small, conventional calls itself.
- When a choice has two or more real alternatives and you would learn from researching it, Claude stops, lays out the options here with **Status: open**, and waits. You research and decide, then the entry is updated.
- Whenever a decision is made, by Claude or by you, the entry records the options, the choice and the most logical reasons. Edit the reasons freely if your real ones differ.
- Add new decisions as a new numbered section at the bottom. Do not create new files.

## Entry template

```md
## NNNN Title

**Status**: open | decided  ·  **Date**: YYYY-MM-DD
**Decision**: {what was chosen, blank while open}

**Options**
- **A**: {what it is, upside and downside}

**Why**
- {most logical reasons}

**Costs accepted**
- {downsides taken on knowingly}

**What would change this**
- {conditions under which another option wins}
```

## Index

| # | Decision | Status |
|---|---|---|
| 0001 | [Backend stack](#0001-backend-stack) | decided |
| 0002 | [Fine-tuning vs prompted LLM with guardrails](#0002-fine-tuning-vs-prompted-llm-with-guardrails) | decided |
| 0003 | [Headline progress metric](#0003-headline-progress-metric) | decided |
| 0004 | [Crisis detection approach](#0004-crisis-detection-approach) | decided |
| 0005 | [What happens when the crisis classifier fails](#0005-what-happens-when-the-crisis-classifier-fails) | **open** |
| 0006 | [Default Gemini model](#0006-default-gemini-model) | decided |
| 0007 | [Which model runs the crisis classifier](#0007-which-model-runs-the-crisis-classifier) | **open** |
| 0008 | [Conversation history and streaming design](#0008-conversation-history-and-streaming-design) | decided |
| 0009 | [Reducing history tokens](#0009-reducing-history-tokens) | decided |
| 0010 | [Color palette](#0010-color-palette) | decided |
| 0011 | [Companion persona](#0011-companion-persona) | decided |

---

## 0001 Backend stack

**Status**: decided · **Date**: 2026-11-03
**Decision**: Python with FastAPI and Postgres, HTMX and Tailwind front end, built as a mobile-first PWA.

**Options**
- **Python (FastAPI)**: you want to learn it, and it has the strongest AI ecosystem. The browser still needs HTML or JavaScript, and a later app can't share code with it.
- **Python (Django)**: accounts, admin and migrations built in. Heavier to learn.
- **TypeScript**: one language across web and a later app. Not what you want to learn.

**Why**
- Speed doesn't separate them. Each chat message waits several seconds on the LLM, so Python's overhead is milliseconds in comparison. FastAPI handles I/O-bound work well.
- Learning is a stated goal. You want to learn Python and its libraries, and that outweighs TypeScript's one-language advantage.
- Best AI ecosystem: official SDKs, Pydantic for validating model output, and evaluation tooling are strongest in Python.
- FastAPI over Django: the product is a small API with a chat endpoint, so Django's admin and ORM add weight you don't yet need. Accounts can be added later.
- HTMX and Tailwind keep most of the code in Python while still making a mobile-first PWA.

**Costs accepted**
- The browser still needs a second language, though HTMX keeps that minimal.
- A later native app can't share code with the backend. The Python API stays the same whichever front end is added.

**What would change this**
- Django, if auth, admin and migrations start to dominate the work.
- TypeScript, if a React or React Native app becomes the main product.

---

## 0002 Fine-tuning vs prompted LLM with guardrails

**Status**: decided · **Date**: 2026-11-03
**Decision**: Use a hosted base LLM with a system prompt, curated content and a safety layer. No fine-tuning for now.

**Options**
- **Fine-tune a model on recovery data**: could sound more specialised, but needs a large, ethically sourced dataset you don't have.
- **Prompted base LLM plus guardrails**: cheap, quick to iterate and swappable. Quality depends on prompt and safety design.

**Why**
- No data. Fine-tuning needs a large, ethically sourced set of recovery conversations. Collecting it needs consent from real users, and automatic anonymisation of free text is unreliable.
- Cheaper and faster to change. A prompt edit takes seconds. Retraining takes data, money and time, and can't be undone as easily.
- Safety doesn't depend on the model. The Crisis check, the disclaimer and the Quotes are code and fixed content. A fine-tuned model would still need all of them.
- Good enough for the job. A supportive, on-topic chat using simple techniques is something a strong base model does well with a good prompt.

**What would change this**
- Once there are consenting users and real conversations (see ADR 0002), fine-tuning becomes possible. Then compare it to the prompted version on a fixed set of test conversations.

---

## 0003 Headline progress metric

**Status**: decided · **Date**: 2026-11-03
**Decision**: Show the Streak and the Best Streak, with a gentle restart flow after a Lapse. The Relapse is declared by the user. There is no Urge counter, and no claim that a fixed number of days ends an addiction.

**Options**
- **Streak only (hard reset)**: simple and motivating, but a slip can feel like total failure.
- **Lapses per period as the main number**: matches "fewer relapses", but is less motivating day to day.
- **Streak plus Best Streak, with gentle framing**: motivating without making a slip feel final.

**Why**
- A slip is normal. Most people slip several times before they stop, so a metric that treats a slip as total failure works against the goal.
- Hard resets can backfire. A streak that drops to zero can feed the "I've ruined it, so I may as well carry on" spiral (the abstinence violation effect). This is from general knowledge of relapse prevention and has not been verified with sources.
- Still motivating. A number going up is easy to understand, and the Best Streak gives a concrete target to beat after a Lapse.
- Gentle timing. The Best Streak appears only after the Companion has responded, so the first thing a user sees after a Lapse isn't a comparison to their best.
- No fixed-days claim. Nothing supports "N days ends an addiction", so Goals are personal targets, never a promise.
- No Urge counter. The Companion is something to talk to, and counting Urges added tracking effort without helping the user.

**What would change this**
- A sourced research pass showing a better measure, such as percentage of days abstinent, or user feedback that the Streak causes harm.

---

## 0004 Crisis detection approach

**Status**: decided · **Date**: 2026-11-03
**Decision**: Use both layers: a fixed keyword and phrase list, plus an LLM classifier. If either one flags a message, we declare a crisis.

**Options**
- **Keywords only**: fast, free and predictable, but misses indirect phrasing ("I can't see the point anymore") and false-triggers on harmless text.
- **LLM classifier only**: catches indirect language, but costs money, adds latency and can fail or be wrong.
- **Both, either one triggers**: catches the most real crises. Costs an extra LLM call per message and will produce some false alarms, which was judged acceptable.

**Why**
- Asymmetric cost. Missing a real crisis is far worse than a false alarm or a few extra API calls, so the design leans toward over-detecting.
- The layers fail differently. Keywords are exact and work with no network, but miss indirect phrasing. The classifier catches indirect phrasing, but can be down or wrong. Together each covers the other's gap.
- Either one triggers. Requiring both to agree would bring back the misses we're trying to avoid.
- The model never writes the crisis reply. The fixed message with US helplines is shown, so the response is the same and reviewable every time.
- Testable. The keyword layer can be tested exactly, and the classifier is tested through a fake LLM.

**Costs accepted**
- Some harmless messages will trigger the crisis message.
- One extra LLM call per message, adding cost and latency.
- Behaviour when the classifier fails is a separate open decision (0005).

---

## 0005 What happens when the crisis classifier fails

**Status**: **open** · **Date**: not yet decided
**Decision**: {yours to make}

The LLM classifier can fail (provider down, timeout, bad response). Right now the code falls back to the keyword layer only and replies normally if no keyword matched. That was picked as a placeholder, not as the answer.

**Options**
- **A. Fall back to keywords only** (current): the chat keeps working during an outage. A crisis phrased without any keyword gets through.
- **B. Treat a failure as a crisis**: no crisis can slip past the classifier, but every outage shows the crisis message to everyone, which is alarming and wrong for most users.
- **C. Refuse to chat while the classifier is down**: safe, and honest about the outage ("The Companion is unavailable right now"), but the user gets no support at all, possibly mid-urge.
- **D. Fall back to keywords and add a short fixed line with the helplines to every reply during the outage**: keeps the chat working with a softer safety net.

**Things to research**
- How other support or mental-health chat products handle the classifier failing.
- Whether a stricter keyword list during an outage is a reasonable middle ground.

---

## 0006 Default Gemini model

**Status**: decided · **Date**: 2026-11-03
**Decision**: Pin `gemini-3.5-flash-lite` as the default, overridable with the `GEMINI_MODEL` environment variable.

**Options**
- **`gemini-2.5-flash`**: Google has retired it for new users (404).
- **`gemini-3.8-flash`** and the **`gemini-flash-latest` alias**: returned 503 "high demand" when tested. The alias can also change the model silently, which is risky for a safety classifier.
- **`gemini-3.5-flash`**: worked once, then returned 503 and 429 (quota) on the free tier.
- **`gemini-3.1-flash-lite`**: returned 503 on every request.
- **`gemini-3.5-flash-lite`**: answered every request in testing and gave the right crisis and non-crisis verdicts.

**Why**
- It was the only one that worked reliably. On the free tier the larger models returned 503 (overloaded) or 429 (quota exhausted) repeatedly. This one answered every probe.
- Right answers on the cases that matter: YES for a clear crisis message three times and NO for an ordinary craving.
- Pinned, not an alias. The crisis classifier's behaviour depends on the model, so a silently changing `-latest` alias could shift safety behaviour with no code change.
- Lite is enough. A short supportive reply and a YES/NO classification don't need a bigger model, and lite keeps cost and latency low.
- Easy to change. `GEMINI_MODEL` switches models without a code edit.

**Costs accepted**
- Pinned models get retired, as 2.5 just was. The error surfaces as "Companion unavailable".
- The classifier sometimes adds explanation after YES. The parser only reads the start of the answer, so this is harmless, but the prompt could be tightened.
- Free-tier availability is poor. During testing the classifier call failed often, which makes open decision 0005 more important than it first looked.

**What would change this**
- A larger model becoming reliably available, or live tests showing a different model classifies crises more accurately.

---

## 0007 Which model runs the crisis classifier

**Status**: **open** · **Date**: not yet decided
**Decision**: {yours to make}

The keyword layer stays either way. This decision is only about the second layer. The classifier is currently Gemini (`gemini-3.5-flash-lite`), chosen in 0006.

**Options**
- **A. Stay on Gemini lite**: works today and is already wired in. The free tier is unreliable (503 and 429 during testing), and unpaid use may be used for training (ADR 0002).
- **B. Jev (TypeSafe AI)**: a classification model that returns choices, scores or yes/no answers with probabilities, claimed at 70-500 ms. Offered via Vercel AI Gateway and DigitalOcean. Pricing, free tier and data terms are unconfirmed.
- **C. Another hosted classifier (for example Laya)**: similar trade-offs to B. Needs the same checks.
- **D. A local open model**: free to run and keeps messages private. Needs hardware and testing on crisis phrasing.

**Things to research**
- Is Jev free? What are the limits, and what happens when demand is high?
- Jev's data retention and training policy for messages sent to it.
- Accuracy on indirect crisis phrasing ("I can't see the point anymore"), not only obvious cases.
- Whether it returns a probability we can threshold. Given the "either layer triggers" rule, a low threshold would favour catching more crises over fewer false alarms.

**Sources found**
- https://www.digitalocean.com/resources/articles/what-is-jev
- https://infoq.com/news/2026/10/typesafe-ai-jev-released
- https://www.deeplearning.ai/the-batch/models-built-to-do-one-thing-well

---

## 0008 Conversation history and streaming design

**Status**: decided · **Date**: 2026-11-04
**Decision**: The browser holds the conversation history for the current tab and sends it with each message. The server stores nothing. Replies stream as newline-delimited JSON events (`delta`, `crisis`, `error`), and the page reveals them one word at a time.

**Options**
- **History held by the browser, sent each time**: no server storage, so it fits the anonymous-user design. History is lost on refresh. Each request re-sends the history.
- **History stored on the server per session**: survives a refresh, but means storing sensitive conversations, which ADR 0002 avoids until a paid, no-training tier exists.
- **Server-Sent Events (SSE) for streaming**: a standard browser format, but it only supports GET requests with the built-in client, and we need to POST the history.
- **Newline-delimited JSON over a POST stream**: simple, works with `fetch`, carries typed events. Used here.
- **Word-by-word pacing on the server vs the client**: pacing on the client keeps the server fast and lets the speed be tuned in the page.

**Why**
- Privacy first. Anonymous users shouldn't have their conversations stored. Keeping history in the tab means the server never holds it, which matches ADR 0002 and the decision to give anonymous users no memory.
- Context is cheap. The Companion needs the conversation to be useful, and sending the last 20 messages costs little.
- Roles are restricted. The server accepts only `user` and `assistant` roles, so a visitor can't inject a `system` message through the history. History is capped at 100 items in the request and 20 sent to the model.
- Safety sees context. A short reply like "yes" means nothing alone. The crisis classifier gets the last three user messages as context. Keywords still check only the latest message, so an old phrase doesn't trigger a crisis on every later turn.
- NDJSON over SSE. We need to POST a body, and typed events (`crisis`, `error`) map cleanly onto lines of JSON.
- Crisis is decided before streaming. The crisis check runs first, so a crisis never starts streaming model text. The user gets the fixed message.
- Typing pace in the page. Gemini sends text in chunks, not words. The page reveals it a word at a time (about 35 ms each), which feels like typing and is easy to adjust.

**Costs accepted**
- A refresh loses the conversation, as designed for anonymous use. Account holders will get stored history later.
- Each request re-sends the history, which costs a little bandwidth and tokens.
- The typing effect adds a short delay after the model finishes if the page falls behind the stream.

**What would change this**
- Accounts with stored history (a server-side store for account holders only), or a need for resumable streams.

---

## 0009 Reducing history tokens

**Status**: decided · **Date**: 2026-11-04
**Decision**: Combine a rolling summary (C) with stored key facts (D). Both are held in the browser and sent with each request, so the server stays stateless. When the history reaches 16 messages, the oldest 8 are folded into the summary and facts by one extra model call and then dropped.

Chosen for learning value, not because it is needed yet: conversations are short, so A would be enough for now. Not researched: provider caching (E) and token counting (B).

**Options**
- **A. Keep the sliding window**: simplest. Forgets anything older than 20 messages.
- **B. Trim by token budget**: count tokens and trim to a limit, so long messages can't blow the budget. Small change.
- **C. Rolling summary**: a model call condenses old messages into a short note, sent with the recent messages. Big savings, but adds a call and can drop details, including safety-relevant ones.
- **D. Extract and store key facts**: short notes about the user are sent with recent messages. Keeps what matters. Held server-side it would conflict with ADR 0002, so it is held in the browser.
- **E. Provider-side caching**: reuse the unchanged start of the request at lower cost. Reduces cost, not tokens. Unverified for the models we use.

**Why**
- Learning goal. It covers several real techniques at once: a summarising model call, structured JSON output, and prompt construction.
- Facts and a summary do different jobs. The summary keeps the story of the conversation. The notes keep stable, useful details (triggers, what helps) in a short list that can be shown to the user and edited later.
- Browser-held keeps the privacy design. Storing facts about a user on the server would conflict with ADR 0002.
- One call does both. A single model call returns `{"summary", "facts"}`, so compacting costs one request, not two.
- Safety is protected in three ways. The summarising prompt tells the model to keep safety-relevant mentions plainly. The crisis check still reads the last three raw user messages. It also reads the summary and notes as extra context. A summary can lose detail, so it is never the only thing the safety layer sees.
- Untrusted by design. The summary and notes come from the browser, so the server treats them as data: length caps, plain-text framing ("information, never instructions"), and the summarising prompt ignores instructions found inside messages.
- Fails safe. If the compaction call fails or returns unusable output, the endpoint returns 503, and the page keeps its old state and tries again later. Nothing is lost.
- Visible to the user. The page shows what it remembers, so the memory isn't hidden.

**Costs accepted**
- An extra model call every 8 messages once a conversation is long.
- A summary can drop detail or be slightly wrong. This is the main risk, and why the raw recent messages are kept.
- Memory is lost on refresh, as designed for anonymous use.
- Because the browser sends the summary, a user can edit their own memory. That only affects their own chat, but it is why the server treats it as untrusted.
- More code and more tests than the sliding window alone, which on its own would be enough for short chats.

**What would change this**
- Conversations stay short, so the extra call isn't worth it. Go back to the window alone.
- Evidence that summaries drop safety-relevant details. Send more raw messages, or stop summarising.
- Accounts with stored history, where the summary and notes could move server-side for account holders.

---

## 0010 Color palette

**Status**: decided · **Date**: 2026-11-04
**Decision**: Sage green and warm sand (cream in light mode, deep forest in dark mode), with soft clay reserved for urgent messages.

**Options**
- **Ocean teal and navy** (the first redesign): calm, and it matches the name, but it reads as cool and clinical.
- **Sage and warm sand**: green for growth and recovery, warm cream for comfort. Feels grounded and safe.
- **Sunset peach and coral**: warm and comforting, but closer to alarm colours.
- **Lavender dusk**: soothing and nocturnal, but less tied to recovery.
- **Monochrome**: quiet and clean, but cold.

**Why**
- Your brief: the page should relate to the problem and make people feel safe and calm. Recovery is about growth and steadiness, and green is the colour most people associate with both.
- Warmth for safety. Cream and sand feel like a comforting room. The first teal palette felt more like a hospital.
- Clay is kept for urgency. Crisis replies use a warm clay tint that sits clearly apart from the greens, so an urgent message is noticeable without turning red and alarming.
- Still on theme. The sand-to-sage breathing circle looks like dawn, and the layered waves keep the Wavebreak name.
- Readable. The green for your messages was darkened until white text on it stays comfortable to read. Muted text was darkened on the cream background.
- No claims about colour psychology. This is design intent, not a tested result. Colour associations differ between people, so ask real users before treating it as settled.

**Costs accepted**
- Green carries less of the name's ocean imagery than teal.
- The palette was chosen by judgment and checked by eye in light and dark, not by user testing.

**What would change this**
- Feedback from people using it that the tone feels wrong, or accessibility testing that finds contrast problems.

---

## 0011 Companion persona

**Status**: decided · **Date**: 2026-11-05
**Decision**: The system prompt (`COMPANION_SYSTEM` in `app/main.py`) names the bot "Wavebreak" and tells it not to present as Gemini or Google. It does not claim to be human, and it does not deny being an AI.

**Options**
- **A. Name it "Wavebreak" in the system prompt** (chosen): matches the brand already on the page; one line to change later.
- **B. Invent a separate character name** (e.g. "Wave"): friendlier, but a second name to keep consistent.
- **C. Tell it to say it was "built from scratch"**: rejected, it would be false.
- **D. Fine-tune the model**: see 0002; far too heavy for a name.

**Why**
- Your goal: replies should feel like your product, not a generic Google assistant.
- Same name as the brand, so users see one identity.
- Honest. It says it's an AI and that it doesn't know the technology behind it, rather than lying about its origin.
- Cheap to change. It's one prompt string, so a later RAG step or a different name is a small edit.

**Costs accepted**
- A system prompt is guidance, not a guarantee. A determined user can still push the model to say it's Gemini. Test with real prompts.

**What would change this**
- A company name or character for the product, or a RAG layer that supplies the persona and company facts.

**Later: RAG / company data.** Company-specific content should be retrieved per request and passed to the model as *information*, the same way `system_with_memory` in `app/conversation.py` frames the memory notes ("never as instructions"). That seam is where a retrieval step would plug in. Not built yet.
