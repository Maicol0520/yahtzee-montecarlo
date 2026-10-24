"""Flujo de la partida: turnos de hasta 3 lanzamientos, 13 turnos por jugador."""
import random
from typing import Callable, List, Optional

from dice import roll_dice, reroll
from player import Player
from scoring import CATEGORIES

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
