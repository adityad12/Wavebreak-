# Backend stack

## What was considered
FastAPI, Django and TypeScript. See `../decisions/0001-backend-stack.md`.

## Why this was chosen
- **Speed doesn't separate them.** Each chat message waits several seconds on the LLM, so Python's overhead is milliseconds in comparison. FastAPI handles I/O-bound work well.
- **Learning is a stated goal.** You want to learn Python and its libraries, and that outweighs TypeScript's one-language advantage.
- **Best AI ecosystem.** Official SDKs, Pydantic for validating model output, and evaluation tooling are strongest in Python.
- **FastAPI over Django.** The product is a small API with a chat endpoint, so Django's built-in admin and ORM add weight you don't yet need. Accounts can be added later.
- **HTMX and Tailwind** keep most of the code in Python while still making a mobile-first PWA.

## Costs accepted
- The browser still needs a second language, though HTMX keeps that minimal.
- A later native app can't share code with the backend. The Python API stays the same whichever front end is added.

## What would change this
- Django, if auth, admin and migrations start to dominate the work.
- TypeScript, if a React or React Native app becomes the main product.
