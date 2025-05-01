"""Policy Proposal Labeler: Likely Panic Language Detector"""

import re
from typing import Optional

PANIC_LABEL = "likely-panic-language"

# Define trigger words, emojis, and punctuation patterns
PANIC_KEYWORDS = [
    "emergency", "breaking", "alert", "urgent", "evacuate", "crisis",
    "do not ignore", "act now", "warning", "immediately", "catastrophe",
    "panic", "danger", "critical", "disaster"
]

PANIC_EMOJIS = ["🚨", "⚠️", "‼️", "❗", "❕"]

class PanicLanguageLabeler:
    """Detects emotionally manipulative or panic-inducing language."""

    def __init__(self, keyword_threshold: int = 2):
        self.keyword_threshold = keyword_threshold

    def _count_panic_signals(self, text: str) -> int:
        score = 0
        lowered = text.lower()

        # Count keyword matches
        for word in PANIC_KEYWORDS:
            if word in lowered:
                score += 1

        # Count emoji presence
        if any(emoji in text for emoji in PANIC_EMOJIS):
            score += 1

        # All-caps words (excluding short acronyms)
        all_caps_words = [w for w in text.split() if w.isupper() and len(w) > 3]
        if len(all_caps_words) >= 1:
            score += 1

        # Excessive punctuation
        if "!!!" in text or "???" in text:
            score += 1

        return score

    def moderate_post(self, text: str) -> Optional[str]:
        """Returns a label if panic signals exceed threshold."""
        if not text:
            return None

        score = self._count_panic_signals(text)
        if score >= self.keyword_threshold:
            return PANIC_LABEL
        return None
