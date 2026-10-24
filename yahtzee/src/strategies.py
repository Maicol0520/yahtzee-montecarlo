"""
Estrategias de juego. Interfaz común:

    choose_keep(dice, rolls_left, card) -> lista de posiciones (0-4) a CONSERVAR
        (con las 5 posiciones = detenerse y no relanzar)
    choose_category(dice, card) -> categoría libre donde anotar
"""
import random
from collections import Counter
from typing import List, Optional, Sequence

from scoring import score
from player import ScoreCard


def _keep_most_frequent(dice: Sequence[int]) -> List[int]:
    counts = Counter(dice)
    best = max(counts, key=lambda v: (counts[v], v))
    return [i for i, d in enumerate(dice) if d == best]


class RandomStrategy:
    """Línea base: conserva dados al azar y anota en una categoría libre al azar."""
    name = "Aleatoria"

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    def choose_keep(self, dice, rolls_left, card: ScoreCard):
        return [i for i in range(5) if self.rng.random() < 0.5]

    def choose_category(self, dice, card: ScoreCard):
        return self.rng.choice(card.available())


class GreedyStrategy:
    """Voraz: conserva el valor más repetido y anota donde más puntos obtiene."""
    name = "Voraz"

    def choose_keep(self, dice, rolls_left, card: ScoreCard):
        return _keep_most_frequent(dice)

    def choose_category(self, dice, card: ScoreCard):
        return max(card.available(), key=lambda c: score(c, dice))


# Puntaje promedio aproximado de cada categoría bajo buen juego.
# Se usa como "valor de referencia" para decidir dónde conviene anotar.
_PAR = {"unos": 2.1, "doses": 5.3, "treses": 8.6, "cuatros": 12.2,
        "cincos": 15.7, "seises": 19.2, "trio": 21.7, "poker": 13.1,
        "full_house": 22.6, "escalera_corta": 29.5, "escalera_larga": 32.7,
        "yahtzee": 16.9, "chance": 22.0}


class HeuristicStrategy:
    """
    Heurística (aporte propio, etapa CREA):
    - Conserva el juego ya hecho (Yahtzee, escalera larga, full house).
    - Persigue escaleras si ya tiene 4 valores consecutivos.
    - Si no, conserva el valor más repetido.
    - Anota donde mayor sea (puntos obtenidos - puntaje de referencia de la categoría).
    """
    name = "Heurística"

    def choose_keep(self, dice, rolls_left, card: ScoreCard):
        avail = set(card.available())
        all_idx = list(range(5))

        if score("yahtzee", dice) > 0:
            return all_idx
        if "escalera_larga" in avail and score("escalera_larga", dice) > 0:
            return all_idx
        if "full_house" in avail and score("full_house", dice) > 0:
            return all_idx

        if avail & {"escalera_corta", "escalera_larga"}:
            values = set(dice)
            target = max(({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}),
                         key=lambda t: len(t & values))
            run = target & values
            if len(run) >= 4:
                if "escalera_larga" not in avail and score("escalera_corta", dice) > 0:
                    return all_idx
                keep, seen = [], set()
                for i, d in enumerate(dice):
                    if d in run and d not in seen:
                        keep.append(i)
                        seen.add(d)
                return keep

        return _keep_most_frequent(dice)

    def choose_category(self, dice, card: ScoreCard):
        return max(card.available(),
                   key=lambda c: (score(c, dice) - _PAR[c], score(c, dice)))
