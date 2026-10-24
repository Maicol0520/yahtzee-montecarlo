#!/usr/bin/env python3
"""
YAHTZEE para 2 jugadores.

Ejecutar:   python yahtzee.py
            python yahtzee.py --seed 7     (partida reproducible)

Cada jugador puede ser Humano o un bot (Aleatorio, Voraz, Heuristico).
"""
import argparse
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence


# ======================================================================
# SCORING
# ======================================================================
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

# ======================================================================
# DICE
# ======================================================================
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

# ======================================================================
# PLAYER
# ======================================================================
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

# ======================================================================
# STRATEGIES
# ======================================================================
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

# ======================================================================
# GAME
# ======================================================================
MAX_ROLLS = 3


class Game:
    def __init__(self, players: List[Player], rng: Optional[random.Random] = None,
                 observer: Optional[Callable] = None):
        self.players = players
        self.rng = rng or random.Random()
        self.observer = observer  # observer(player, dice, category, points)

    def play_turn(self, player: Player) -> None:
        dice = roll_dice(rng=self.rng)
        for rolls_left in range(MAX_ROLLS - 1, 0, -1):   # quedan 2 y luego 1
            keep = player.strategy.choose_keep(dice, rolls_left, player.card)
            if len(set(keep)) >= len(dice):
                break                                    # se detiene antes
            dice = reroll(dice, keep, self.rng)
        category = player.strategy.choose_category(dice, player.card)
        points = player.card.record(category, dice)
        if self.observer:
            self.observer(player, dice, category, points)

    def play(self) -> dict:
        for _ in range(len(CATEGORIES)):                 # 13 rondas
            for player in self.players:
                self.play_turn(player)
        return self.result()

    def result(self) -> dict:
        totals = {p.name: p.card.total() for p in self.players}
        best = max(totals.values())
        winners = [n for n, t in totals.items() if t == best]
        return {"totals": totals, "winner": winners[0] if len(winners) == 1 else None}

# ======================================================================
# CLI
# ======================================================================
def show_dice(dice):
    return "  ".join(f"[{i + 1}]={d}" for i, d in enumerate(dice))


def show_scorecards(players):
    print("\n" + "=" * (22 + 16 * len(players)))
    print(f"{'Categoría':<22}" + "".join(f"{p.name:>16}" for p in players))
    print("-" * (22 + 16 * len(players)))
    for c in CATEGORIES:
        row = f"{NAMES[c]:<22}"
        for p in players:
            v = p.card.scores[c]
            row += f"{('-' if v is None else v):>16}"
        print(row)
    print("-" * (22 + 16 * len(players)))
    print(f"{'Subtotal superior':<22}" + "".join(f"{p.card.upper_subtotal():>16}" for p in players))
    print(f"{'Bono (>=63)':<22}" + "".join(f"{p.card.upper_bonus():>16}" for p in players))
    print(f"{'TOTAL':<22}" + "".join(f"{p.card.total():>16}" for p in players))
    print("=" * (22 + 16 * len(players)))


class HumanStrategy:
    name = "Humano"

    def choose_keep(self, dice, rolls_left, card):
        print(f"\nDados: {show_dice(dice)}   (relanzamientos restantes: {rolls_left})")
        while True:
            text = input("Posiciones a CONSERVAR (ej. 1 3 5; Enter = relanzar todos; "
                         "t = conservar todos y anotar): ").strip().lower()
            if text == "t":
                return list(range(5))
            if all(ch in "12345 ,;" for ch in text):
                return [int(ch) - 1 for ch in set(text) if ch in "12345"]
            print("Entrada no válida.")

    def choose_category(self, dice, card):
        avail = card.available()
        print(f"\nDados finales: {show_dice(dice)}")
        for n, c in enumerate(avail, 1):
            print(f"  {n:>2}. {NAMES[c]:<16} -> {score(c, dice)} pts")
        while True:
            text = input("Elige categoría (número): ").strip()
            if text.isdigit() and 1 <= int(text) <= len(avail):
                return avail[int(text) - 1]
            print("Opción no válida.")


BOTS = {"1": RandomStrategy, "2": GreedyStrategy, "3": HeuristicStrategy}


def ask_player(idx, rng):
    print(f"\nJugador {idx}:  [h] Humano   [1] Aleatorio   [2] Voraz   [3] Heurístico")
    while True:
        choice = input("Tipo: ").strip().lower()
        if choice == "h":
            name = input("Nombre: ").strip() or f"Jugador {idx}"
            return Player(name, HumanStrategy())
        if choice in BOTS:
            cls = BOTS[choice]
            strategy = cls(rng) if cls is RandomStrategy else cls()
            return Player(f"{strategy.name} {idx}", strategy)
        print("Opción no válida.")


def main():
    parser = argparse.ArgumentParser(description="Yahtzee para 2 jugadores")
    parser.add_argument("--seed", type=int, default=None, help="semilla aleatoria")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    print("=== YAHTZEE (2 jugadores) ===")
    players = [ask_player(1, rng), ask_player(2, rng)]

    def observer(player, dice, category, points):
        if not isinstance(player.strategy, HumanStrategy):
            print(f"{player.name}: {show_dice(dice)} -> {NAMES[category]} (+{points})")
        else:
            print(f"-> {NAMES[category]} (+{points})")

    game = Game(players, rng=rng, observer=observer)
    result = game.play()
    show_scorecards(players)
    print("Resultado:", "EMPATE" if result["winner"] is None else f"gana {result['winner']}")


if __name__ == "__main__":
    main()
