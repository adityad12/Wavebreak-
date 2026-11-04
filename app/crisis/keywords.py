import re

_PHRASES = [
    r"kill myself",
    r"killing myself",
    r"end my life",
    r"ending my life",
    r"take my own life",
    r"suicid\w*",
    r"want to die",
    r"wanna die",
    r"better off dead",
    r"no reason to live",
    r"can'?t go on",
    r"hurt myself",
    r"harm myself",
    r"self[- ]?harm",
    r"cut myself",
    r"overdos\w*",
    r"withdrawal seizure\w*",
]

_PATTERN = re.compile(r"\b(?:" + "|".join(_PHRASES) + r")\b", re.IGNORECASE)


def keyword_hits(text: str) -> list[str]:
    return [m.group(0).lower() for m in _PATTERN.finditer(text)]
