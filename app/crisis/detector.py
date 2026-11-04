import logging
from dataclasses import dataclass, field
from typing import Protocol

from app.crisis.keywords import keyword_hits

log = logging.getLogger(__name__)


class CrisisClassifier(Protocol):
    async def is_crisis(self, text: str, context: list[str] | None = None) -> bool: ...


@dataclass
class CrisisResult:
    is_crisis: bool
    keyword_hits: list[str] = field(default_factory=list)
    classifier_flagged: bool = False
    classifier_failed: bool = False


class CrisisDetector:
    """Declares a crisis if either the keyword layer or the classifier flags it."""

    def __init__(self, classifier: CrisisClassifier):
        self._classifier = classifier

    async def check(self, text: str, context: list[str] | None = None) -> CrisisResult:
        # Keywords look at the latest message only, so one early hit doesn't
        # re-trigger on every later turn. The classifier also sees recent context.
        hits = keyword_hits(text)
        flagged = False
        failed = False
        try:
            flagged = await self._classifier.is_crisis(text, context)
        except Exception:
            # On failure we fall back to keywords only; see docs/decisions/0005.
            log.exception("Crisis classifier failed")
            failed = True
        return CrisisResult(
            is_crisis=bool(hits) or flagged,
            keyword_hits=hits,
            classifier_flagged=flagged,
            classifier_failed=failed,
        )
