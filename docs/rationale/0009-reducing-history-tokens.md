# How to reduce tokens sent while keeping context

## What was considered
Sliding window, token budget, rolling summary, stored facts and provider caching. See `../decisions/0009-reducing-history-tokens.md`.

## Why this was chosen
- **Learning goal.** You chose this to learn as much as possible. It covers several real techniques at once: a summarising model call, structured JSON output, and prompt construction.
- **Facts and a summary do different jobs.** The summary keeps the story of the conversation. The notes keep stable, useful details (triggers, what helps) in a short list that can be shown to the user and edited later.
- **Browser-held keeps the privacy design.** Storing facts about a user on the server would conflict with ADR 0002. Keeping the summary and notes in the tab and sending them each time means the server still stores nothing.
- **One call does both.** A single model call returns `{"summary", "facts"}`, so compacting costs one request, not two.
- **Safety is protected in three ways.** The summarising prompt tells the model to keep safety-relevant mentions plainly. The crisis check still reads the last three raw user messages. It also reads the summary and notes as extra context. A summary can lose detail, so it is never the only thing the safety layer sees.
- **Untrusted by design.** The summary and notes come from the browser, so the server treats them as data: length caps, plain-text framing ("information, never instructions"), and the summarising prompt ignores instructions found inside messages.
- **Fails safe.** If the compaction call fails or returns unusable output, the endpoint returns 503, and the page keeps its old state and tries again later. Nothing is lost.
- **Visible to the user.** The page shows what it remembers, so the memory isn't hidden.

## Costs accepted
- An extra model call every 8 messages once a conversation is long.
- A summary can drop detail or be slightly wrong. This is the main risk, and why the raw recent messages are kept.
- Memory is lost on refresh, as designed for anonymous use.
- Because the browser sends the summary, a user can edit their own memory. That only affects their own chat, but it is why the server treats it as untrusted.
- More code and more tests than the sliding window alone, which on its own would be enough for short chats.

## What would change this
- Conversations stay short, so the extra call isn't worth it. Go back to the window alone.
- Evidence that summaries drop safety-relevant details. Send more raw messages, or stop summarising.
- Accounts with stored history, where the summary and notes could move server-side for account holders.
