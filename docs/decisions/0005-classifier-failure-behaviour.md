# What happens when the crisis classifier fails

**Status**: open
**Decision**: {yours to make}

The LLM classifier can fail (provider down, timeout, bad response). Right now the code falls back to the keyword layer only and replies normally if no keyword matched. I picked that as a placeholder, not as the answer.

## Options
- **A. Fall back to keywords only** (current): the chat keeps working during an outage. A crisis phrased without any keyword gets through.
- **B. Treat a failure as a crisis**: no crisis can slip past the classifier, but every outage shows the crisis message to everyone, which is alarming and wrong for most users.
- **C. Refuse to chat while the classifier is down**: safe, and honest about the outage ("The Companion is unavailable right now"), but the user gets no support at all, possibly mid-urge.
- **D. Fall back to keywords and add a short fixed line with the helplines to every reply during the outage**: keeps the chat working with a softer safety net.

## Things to research
- How other support or mental-health chat products handle the classifier failing.
- Whether a stricter keyword list during an outage is a reasonable middle ground.

## Date decided
{YYYY-MM-DD}
