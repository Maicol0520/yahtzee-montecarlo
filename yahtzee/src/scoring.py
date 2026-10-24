"""Reglas de puntuación del Yahtzee clásico (sin bono de Yahtzee extra ni comodines)."""
from collections import Counter
from typing import Sequence

UPPER_VALUES = {"unos": 1, "doses": 2, "treses": 3,
                "cuatros": 4, "cincos": 5, "seises": 6}
LOWER_CATEGORIES = ["trio", "poker", "full_house", "escalera_corta",
                    "escalera_larga", "yahtzee", "chance"]
CATEGORIES = list(UPPER_VALUES) + LOWER_CATEGORIES

NAMES = {
    "unos": "Unos", "doses": "Doses", "treses": "Treses", "cuatros": "Cuatros",
    "cincos": "Cincos", "seises": "Seises", "trio": "Trío", "poker": "Póker",
    "full_house": "Full house", "escalera_corta": "Escalera corta",
    "escalera_larga": "Escalera larga", "yahtzee": "Yahtzee", "chance": "Chance",
}

UPPER_BONUS_THRESHOLD = 63
UPPER_BONUS = 35
FULL_HOUSE_POINTS = 25
SMALL_STRAIGHT_POINTS = 30
LARGE_STRAIGHT_POINTS = 40
YAHTZEE_POINTS = 50

_SMALL_STRAIGHTS = ({1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6})
_LARGE_STRAIGHTS = ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6})


def score(category: str, dice: Sequence[int]) -> int:
    """Puntaje que obtendrían `dice` si se anotan en `category`."""
    if category not in CATEGORIES:
        raise ValueError(f"Categoría desconocida: {category}")
    counts = Counter(dice)
    total = sum(dice)

    if category in UPPER_VALUES:
        v = UPPER_VALUES[category]
        return v * counts[v]
    if category == "trio":
        return total if max(counts.values()) >= 3 else 0
    if category == "poker":
        return total if max(counts.values()) >= 4 else 0
    if category == "full_house":
        return FULL_HOUSE_POINTS if sorted(counts.values()) == [2, 3] else 0
    if category == "escalera_corta":
        values = set(dice)
        return SMALL_STRAIGHT_POINTS if any(s <= values for s in _SMALL_STRAIGHTS) else 0
    if category == "escalera_larga":
        return LARGE_STRAIGHT_POINTS if set(dice) in _LARGE_STRAIGHTS else 0
    if category == "yahtzee":
        return YAHTZEE_POINTS if len(counts) == 1 else 0
    return total  # chance
