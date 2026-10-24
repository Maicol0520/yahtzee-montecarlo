"""Tarjeta de puntajes y jugador."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from scoring import (CATEGORIES, UPPER_VALUES, UPPER_BONUS,
                     UPPER_BONUS_THRESHOLD, score)


class ScoreCard:
    def __init__(self) -> None:
        self.scores: Dict[str, Optional[int]] = {c: None for c in CATEGORIES}

    def available(self) -> List[str]:
        return [c for c, v in self.scores.items() if v is None]

    def record(self, category: str, dice: Sequence[int]) -> int:
        if category not in self.scores or self.scores[category] is not None:
            raise ValueError(f"Categoría no disponible: {category}")
        pts = score(category, dice)
        self.scores[category] = pts
        return pts

    def upper_subtotal(self) -> int:
        return sum(self.scores[c] or 0 for c in UPPER_VALUES)

    def upper_bonus(self) -> int:
        return UPPER_BONUS if self.upper_subtotal() >= UPPER_BONUS_THRESHOLD else 0

    def total(self) -> int:
        return sum(v or 0 for v in self.scores.values()) + self.upper_bonus()

    def is_complete(self) -> bool:
        return not self.available()


@dataclass
class Player:
    name: str
    strategy: object
    card: ScoreCard = field(default_factory=ScoreCard)
