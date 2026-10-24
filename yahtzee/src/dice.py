"""Lanzamiento de dados (distribución uniforme discreta sobre 1..6)."""
import random
from typing import List, Optional, Sequence

NUM_DICE = 5
NUM_SIDES = 6


def roll_dice(n: int = NUM_DICE, rng: Optional[random.Random] = None) -> List[int]:
    """Lanza n dados de seis caras."""
    rng = rng or random
    return [rng.randint(1, NUM_SIDES) for _ in range(n)]


def reroll(dice: Sequence[int], keep: Sequence[int],
           rng: Optional[random.Random] = None) -> List[int]:
    """Relanza todos los dados excepto los de las posiciones `keep` (0-4)."""
    rng = rng or random
    keep = set(keep)
    return [d if i in keep else rng.randint(1, NUM_SIDES) for i, d in enumerate(dice)]
