# How an LLM remembers a conversation

**Mission link:** you want to explain how Wavebreak's Companion remembers what you told it, and change that behaviour safely.
**One win:** by the end you can say why the model forgot everything before, and point to the four places in our code that fixed it.

## 1. The core idea: the model has no memory

A language model is a function. You give it text, it gives back text, and then it forgets. Nothing from your last request is kept inside the model.

Google's docs say it directly: the REST API is stateless, so you pass the full conversation history in the request ([Gemini text generation docs](https://ai.google.dev/gemini-api/docs/generate-content/text-generation)).

So "memory" is something **our app** builds. Each time you send a message, we re-send the earlier messages along with it, and the model reads the whole conversation again from the top.

**Why Wavebreak forgot before:** the first version sent only the new message.

```python
# before: the model only ever saw this one string
await self._client.aio.models.generate_content(model=..., contents=user, ...)
```

## 2. The shape of the history

History is a list of turns. Each turn has a **role** and some **text**.

| Role in our code | Role Gemini expects | Who wrote it |
|---|---|---|
| `user` | `user` | the person |
| `assistant` | `model` | the AI's earlier reply |

The docs say the role must be `user` or `model`, and the turns should alternate. Our code uses the name `assistant` (common across providers) and translates it for Gemini.

A conversation of three turns looks like this:

```python
[
    Message("user", "I smoke when I'm stressed at work"),
    Message("assistant", "That sounds hard. What happens next?"),
    Message("user", "so what do I do?"),     # the new message, last
]
```

The model reads all three and answers the last one **in light of the first two**. That is the whole trick.

## 3. How Wavebreak does it, in four steps

### Step A: the browser keeps the list (`app/static/index.html`)

```javascript
const history = [];  // this tab only; sent with each message so the Companion has context
...
body: JSON.stringify({ message, history })
...
if (reply) history.push({ role: "user", content: message }, { role: "assistant", content: reply });
```

After each exchange the page adds your message and the reply to `history`. The next request sends it back. Refresh the page and the list is gone.

### Step B: the server accepts it, with limits (`app/main.py`)

```python
class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[HistoryItem] = Field(default_factory=list, max_length=100)
```

`Literal["user", "assistant"]` means a visitor cannot send a `system` turn such as "ignore your rules". Anything else is rejected with a 422 error.

### Step C: trim and tidy it before sending (`app/conversation.py`)

```python
MAX_HISTORY = 20

def build_messages(history, message):
    recent = history[-MAX_HISTORY:]
    while recent and recent[0].role != "user":
        recent = recent[1:]          # the model's turn must not come first
    return [*recent, Message("user", message)]
```

- `history[-20:]` keeps only the last 20 messages. Why? See section 4.
- The `while` loop handles a side effect of trimming: cutting the list can leave an `assistant` turn first, and a conversation should start with the user.
- The new message goes on the end.

### Step D: translate and send (`app/gemini.py`)

```python
contents = [
    types.Content(
        role="user" if m.role == "user" else "model",
        parts=[types.Part(text=m.content)],
    )
    for m in messages
]
stream = await self._client.aio.models.generate_content_stream(
    model=self._model, contents=contents,
    config=types.GenerateContentConfig(system_instruction=system),
)
```

Our `Message` objects become Gemini's `Content` objects, then the whole list goes out.

**The system prompt is separate.** `system_instruction` holds the Companion's rules ("warm, calm, never claim to be a therapist"). It isn't one of the turns. We send it with every request too, because the model forgets it just like everything else.

## 4. Why not send everything forever?

Models read text in **tokens** (roughly word pieces), and each model has a **context window**, a limit on how many tokens it can read in one request. Everything counts toward it, including the system instruction ([token docs](https://ai.google.dev/gemini-api/docs/tokens)).

- **Cost:** you pay for every token you send, every time, including old history.
- **Speed:** more input means a slower start to the reply.
- **Limit:** very long chats eventually don't fit.
- **Focus:** long context is available ([long context docs](https://ai.google.dev/gemini-api/docs/long-context)), but a small, recent window is simpler and cheaper.

That is why `MAX_HISTORY = 20`. The trade-off is that the Companion forgets what you said 21 messages ago. A common fix, which we haven't built, is to summarise old messages into a short note.

## 5. Where context also matters: the crisis check

The safety classifier is a **second, separate model call**, so it also forgets. If you say "I've been thinking of ending things" and then just "yes", the second message alone looks harmless.

So `classifier_context` gives it the last three user messages:

```python
def classifier_context(history):
    user_texts = [m.content for m in history if m.role == "user"]
    return user_texts[-3:]
```

The keyword check still reads only the latest message. Otherwise one old phrase would trigger the crisis reply on every later turn.

## 6. Stateless vs stored history

We chose to have the browser hold the history and the server store nothing (decision [0008](../decisions/0008-stateless-history-and-streaming.md)). The alternative is for the server to remember the conversation. Google's newer Interactions API does this for you with `previous_interaction_id`, and it also shows the stateless pattern with `store=False` ([migration guide](https://ai.google.dev/gemini-api/docs/migrate-to-interactions)).

For Wavebreak, stored chats would mean holding sensitive conversations. That's why stateless won (see ADR [0002](../adr/0002-no-real-user-data-until-paid-llm-tier.md)).

## 7. Remembering more without sending more: summary and notes

The 20-message window forgets older messages. To keep the gist, we added two things (decision [0009](../decisions/0009-reducing-history-tokens.md)):

- a **rolling summary**: a short paragraph of what the conversation was about
- **notes**: a short list of facts worth keeping (triggers, what helps)

When the page's history reaches 16 messages, it sends the oldest 8 to `/chat/memory`. One extra model call returns updated JSON, and the page then drops those 8 messages:

```javascript
const n = history.length - KEEP_RECENT;
const r = await fetch("/chat/memory", { ..., body: JSON.stringify({ summary, facts, messages: history.slice(0, n) }) });
if (r.ok) { summary = d.summary; facts = d.facts; history.splice(0, n); }
```

On the next message, `system_with_memory` (`app/conversation.py`) adds them to the system prompt as background, and the model sees: rules, then what we remember, then the recent messages.

Three things to notice:

- **The model call returns text, so we parse it.** `parse_memory` (`app/memory.py`) strips code fences, checks the shape, and clamps the size. If the model's answer isn't usable, we raise an error and keep the old memory. Never trust model output to be well-formed.
- **The memory comes from the browser, so it is untrusted.** The server caps its length and tells the model to treat it as information, never as instructions.
- **A summary can lose things.** For safety, the crisis check still reads the last three raw user messages plus the summary. It never relies on the summary alone.

## Check yourself (try to answer before opening each one)

**Q1.** You send "What's my name?" with an empty history. What happens?

<details><summary>Answer</summary>

The model has no way to know. It sees one message with no earlier turns, so it will guess, ask you, or say it can't know. Memory only exists if you send it.

</details>

**Q2.** Which of these stops a visitor from sneaking a fake `system` message into the history?

- A. The `MAX_HISTORY` limit on turns
- B. The `Literal` role check on input
- C. The `while` loop in the builder
- D. The `max_length` cap on text

<details><summary>Answer</summary>

B. `Literal["user", "assistant"]` rejects any other role before the code runs. The other three control size and order, not who is speaking.

</details>

**Q3.** After 30 exchanges, what does the model see of message number 1?

<details><summary>Answer</summary>

Nothing. Only the last 20 messages are sent, so message 1 is cut. The Companion has forgotten it, unless a summary were added.

</details>

**Q4.** Why does the crisis check get context but the keyword check does not?

<details><summary>Answer</summary>

A short reply like "yes" can only be judged with earlier messages, so the classifier needs them. The keyword check scans for exact phrases, and scanning old messages would re-trigger a crisis on every later turn.

</details>

**Q5.** Why does the crisis check get the summary as well as the last three raw messages?

<details><summary>Answer</summary>

A summary can lose or soften details, so it shouldn't be the only thing the safety layer relies on. The raw recent messages show the exact words. The summary adds older context that the raw messages no longer contain. Together they cover more than either alone.

</details>

## Try it yourself (about 10 minutes)

1. Open **http://127.0.0.1:8000**. Tell the Companion a made-up fact ("my cat is called Pixel"), send two other messages, then ask "what's my cat's name?" It should remember.
2. Refresh the page and ask again. It forgets. Why? (Section 3, step A.)
3. In `app/conversation.py`, set `MAX_HISTORY = 2`, restart the server, and repeat step 1. What breaks? Put it back to 20 afterwards.
4. Run `python -m pytest tests/unit/test_conversation.py` before and after step 3, and see which test fails.
5. Send about 10 messages of a made-up story (say, a stressful job and an evening habit). After the 16th history entry, a "What I remember from earlier in this chat" box appears. Open it. Is anything wrong or missing? Why might that matter for safety?

## Primary source

Read the section on multi-turn conversations in the [Gemini text generation docs](https://ai.google.dev/gemini-api/docs/generate-content/text-generation). It is the official description of `contents`, roles and why you send the full history. Those pages are marked "Legacy", so check the current docs for model names and the newer Interactions API.

## Ask follow-up questions

I'm your teacher here. If anything is unclear, ask me, for example: "show me what the request looks like on the wire", "how would summarising old messages work", or "what is a token exactly".

## Glossary

- **Stateless:** the server keeps nothing between requests.
- **Context window:** the most text, in tokens, the model can read in one request.
- **Token:** a piece of a word, the unit models read and you pay for.
- **System instruction:** standing rules sent with every request, separate from the turns.
- **Turn / message:** one entry in the history, with a role and text.
- **Role:** who wrote a turn: `user`, or `assistant` (`model` in Gemini).
