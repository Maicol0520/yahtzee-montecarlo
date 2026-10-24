import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from game import Game
from player import Player, ScoreCard
from scoring import CATEGORIES
from strategies import RandomStrategy, GreedyStrategy, HeuristicStrategy


def make_players(seed):
    rng = random.Random(seed)
    return [Player("A", RandomStrategy(rng)), Player("B", HeuristicStrategy())], rng


def test_partida_completa_13_categorias():
    players, rng = make_players(1)
    result = Game(players, rng).play()
    for p in players:
        assert p.card.is_complete()
        assert len(p.card.scores) == 13
    assert set(result["totals"]) == {"A", "B"}


def test_reproducible_con_semilla():
    r1 = Game(*make_players(7)).play()
    r2 = Game(*make_players(7)).play()
    assert r1 == r2


def test_no_se_puede_repetir_categoria():
    card = ScoreCard()
    card.record("chance", [1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        card.record("chance", [1, 1, 1, 1, 1])


def test_bono_superior():
    card = ScoreCard()
    card.record("unos", [1, 1, 1, 2, 2])      # 3
    card.record("doses", [2, 2, 2, 1, 1])     # 6
    card.record("treses", [3, 3, 3, 1, 1])    # 9
    card.record("cuatros", [4, 4, 4, 1, 1])   # 12
    card.record("cincos", [5, 5, 5, 1, 1])    # 15
    card.record("seises", [6, 6, 6, 1, 1])    # 18 -> subtotal 63
    assert card.upper_subtotal() == 63
    assert card.upper_bonus() == 35
    assert card.total() == 63 + 35


def test_maximo_tres_lanzamientos():
    contador = {"n": 0}

    class Contador(GreedyStrategy):
        def choose_keep(self, dice, rolls_left, card):
            contador["n"] += 1
            return []          # siempre pide relanzar todo

    game = Game([Player("X", Contador())], random.Random(0))
    game.play_turn(game.players[0])
    assert contador["n"] == 2   # 2 decisiones de relanzar = 3 lanzamientos en total
