import itertools
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from scoring import score, CATEGORIES


def test_categorias_superiores():
    assert score("unos", [1, 1, 3, 4, 5]) == 2
    assert score("seises", [6, 6, 6, 2, 1]) == 18
    assert score("cincos", [1, 2, 3, 4, 6]) == 0


def test_trio_poker():
    assert score("trio", [3, 3, 3, 4, 5]) == 18
    assert score("trio", [3, 3, 4, 4, 5]) == 0
    assert score("poker", [2, 2, 2, 2, 6]) == 14
    assert score("poker", [2, 2, 2, 6, 6]) == 0


def test_full_house():
    assert score("full_house", [2, 2, 3, 3, 3]) == 25
    assert score("full_house", [2, 2, 2, 2, 3]) == 0
    assert score("full_house", [4, 4, 4, 4, 4]) == 0   # Yahtzee no es full (sin comodín)


def test_escaleras():
    assert score("escalera_corta", [1, 2, 3, 4, 6]) == 30
    assert score("escalera_corta", [3, 4, 5, 6, 6]) == 30
    assert score("escalera_corta", [1, 2, 4, 5, 6]) == 0
    assert score("escalera_larga", [1, 2, 3, 4, 5]) == 40
    assert score("escalera_larga", [6, 5, 4, 3, 2]) == 40
    assert score("escalera_larga", [1, 2, 3, 4, 6]) == 0


def test_yahtzee_y_chance():
    assert score("yahtzee", [5, 5, 5, 5, 5]) == 50
    assert score("yahtzee", [5, 5, 5, 5, 4]) == 0
    assert score("chance", [1, 2, 3, 4, 6]) == 16


def test_categoria_invalida():
    with pytest.raises(ValueError):
        score("inexistente", [1, 2, 3, 4, 5])


def test_conteo_exhaustivo_coincide_con_teoria():
    """Verifica por enumeración de los 6^5 = 7776 resultados las probabilidades teóricas."""
    yz = lg = fh = pk = 0
    for d in itertools.product(range(1, 7), repeat=5):
        yz += score("yahtzee", d) > 0
        lg += score("escalera_larga", d) > 0
        fh += score("full_house", d) > 0
        pk += score("poker", d) > 0 and score("yahtzee", d) == 0   # 4 iguales exactos
    assert (yz, lg, fh, pk) == (6, 240, 300, 150)
