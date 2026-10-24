"""Interfaz de consola: humano vs humano, humano vs computador, computador vs computador."""
import argparse
import random

from game import Game
from player import Player
from scoring import CATEGORIES, NAMES, score
from strategies import GreedyStrategy, HeuristicStrategy, RandomStrategy


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
