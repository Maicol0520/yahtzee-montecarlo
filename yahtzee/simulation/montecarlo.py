"""
Simulación de Montecarlo para verificar la Ley de los Grandes Números (LGN).

Experimento 1: frecuencia relativa de eventos en un lanzamiento de 5 dados vs. N.
Experimento 2: puntaje promedio por partida de cada estrategia vs. número de partidas.
Experimento 3: tasa de victorias entre estrategias vs. número de partidas.

Uso:  python simulation/montecarlo.py --rolls-exp 6 --games 5000 --seed 42
"""
import argparse
import csv
import math
import os
import random
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from dice import roll_dice                                   # noqa: E402
from game import Game                                        # noqa: E402
from player import Player                                    # noqa: E402
from scoring import score                                    # noqa: E402
from strategies import RandomStrategy, GreedyStrategy, HeuristicStrategy  # noqa: E402

# Probabilidades teóricas con 6^5 = 7776 resultados equiprobables
THEORY = {
    "yahtzee": 6 / 7776,
    "escalera_larga": 240 / 7776,
    "full_house": 300 / 7776,
    "poker_exacto": 150 / 7776,
}
LABELS = {"yahtzee": "Yahtzee", "escalera_larga": "Escalera larga",
          "full_house": "Full house", "poker_exacto": "Póker exacto"}
THEORY_MEAN_SUM = 17.5


def _events(dice):
    counts = Counter(dice)
    return {
        "yahtzee": len(counts) == 1,
        "escalera_larga": score("escalera_larga", dice) > 0,
        "full_house": score("full_house", dice) > 0,
        "poker_exacto": max(counts.values()) == 4,
    }


# ---------------------------------------------------------------- Experimento 1
def experiment_single_roll(max_exp, seed, out_dir):
    rng = random.Random(seed)
    n_max = 10 ** max_exp
    checkpoints = sorted(set(int(round(10 ** x)) for x in np.linspace(2, max_exp, 60))
                         | {10 ** k for k in range(2, max_exp + 1)})
    cp_set = set(checkpoints)
    hits = Counter()
    total_sum = 0
    rows = []

    for i in range(1, n_max + 1):
        dice = roll_dice(rng=rng)
        total_sum += sum(dice)
        for ev, ok in _events(dice).items():
            if ok:
                hits[ev] += 1
        if i in cp_set:
            row = {"N": i, "media_suma": total_sum / i}
            for ev in THEORY:
                row[f"freq_{ev}"] = hits[ev] / i
            rows.append(row)

    # CSV completo
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "exp1_lanzamientos.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # Tabla resumen en potencias de 10
    print("\n=== Experimento 1: un lanzamiento de 5 dados ===")
    header = f"{'N':>9} | " + " | ".join(f"{LABELS[e]:>14}" for e in THEORY) + f" | {'Media suma':>10}"
    print(header)
    for r in rows:
        if r["N"] in {10 ** k for k in range(2, max_exp + 1)}:
            print(f"{r['N']:>9} | " + " | ".join(f"{100 * r['freq_' + e]:>13.4f}%" for e in THEORY)
                  + f" | {r['media_suma']:>10.4f}")
    print(f"{'Teórico':>9} | " + " | ".join(f"{100 * p:>13.4f}%" for p in THEORY.values())
          + f" | {THEORY_MEAN_SUM:>10.4f}")

    ns = np.array([r["N"] for r in rows])

    # Figura 1: frecuencias vs N
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for ax, ev in zip(axes.ravel(), THEORY):
        ax.semilogx(ns, [100 * r[f"freq_{ev}"] for r in rows], lw=1.6, label="Frecuencia observada")
        ax.axhline(100 * THEORY[ev], color="red", ls="--", label="Probabilidad teórica")
        ax.set_title(LABELS[ev]); ax.set_xlabel("N (lanzamientos)"); ax.set_ylabel("Frecuencia (%)")
        ax.grid(alpha=.3)
    axes[0, 0].legend()
    fig.suptitle("Convergencia de la frecuencia relativa a la probabilidad teórica")
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "fig1_frecuencias.png"), dpi=150); plt.close(fig)

    # Figura 2: error absoluto vs N (log-log) con referencia sqrt(p(1-p)/N)
    fig, ax = plt.subplots(figsize=(8, 5))
    for ev, color in zip(THEORY, ["C0", "C1", "C2", "C3"]):
        p = THEORY[ev]
        err = [abs(r[f"freq_{ev}"] - p) for r in rows]
        ax.loglog(ns, err, color=color, alpha=.8, label=f"|error| {LABELS[ev]}")
        ax.loglog(ns, np.sqrt(p * (1 - p) / ns), color=color, ls=":", lw=1.2)
    ax.set_xlabel("N (lanzamientos)"); ax.set_ylabel("Error absoluto")
    ax.set_title("Error absoluto vs N (punteado: desviación estándar teórica √(p(1-p)/N))")
    ax.grid(alpha=.3, which="both"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "fig2_error.png"), dpi=150); plt.close(fig)

    # Figura 3: media de la suma
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.semilogx(ns, [r["media_suma"] for r in rows], lw=1.6, label="Media muestral")
    ax.axhline(THEORY_MEAN_SUM, color="red", ls="--", label="Valor esperado 17.5")
    ax.set_xlabel("N (lanzamientos)"); ax.set_ylabel("Suma promedio de los 5 dados")
    ax.set_title("LGN: la media muestral converge al valor esperado"); ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "fig3_media_suma.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- Experimento 2
def _build(name, rng):
    return {"Aleatoria": lambda: RandomStrategy(rng),
            "Voraz": GreedyStrategy,
            "Heurística": HeuristicStrategy}[name]()


def experiment_scores(n_games, seed, out_dir):
    print("\n=== Experimento 2: puntaje por partida de cada estrategia ===")
    fig, ax = plt.subplots(figsize=(8, 5))
    rows = []
    for k, name in enumerate(["Aleatoria", "Voraz", "Heurística"]):
        rng = random.Random(seed + k)
        scores = []
        for _ in range(n_games):
            players = [Player("A", _build(name, rng)), Player("B", _build(name, rng))]
            res = Game(players, rng).play()
            scores.extend(res["totals"].values())      # 2 puntajes independientes por partida
        arr = np.array(scores, dtype=float)
        running = np.cumsum(arr) / np.arange(1, len(arr) + 1)
        mean, sd = arr.mean(), arr.std(ddof=1)
        ci = 1.96 * sd / math.sqrt(len(arr))
        rows.append((name, len(arr), mean, sd, ci))
        ax.semilogx(np.arange(1, len(arr) + 1), running, lw=1.4,
                    label=f"{name} (media final {mean:.1f})")
    print(f"{'Estrategia':<12} | {'n':>7} | {'Media':>8} | {'Desv.':>7} | {'IC 95% ±':>9}")
    for name, n, mean, sd, ci in rows:
        print(f"{name:<12} | {n:>7} | {mean:>8.2f} | {sd:>7.2f} | {ci:>9.2f}")
    with open(os.path.join(out_dir, "exp2_puntajes.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["estrategia", "n", "media", "desv_est", "ic95_mitad"])
        w.writerows(rows)
    ax.set_xlabel("Número de puntajes simulados"); ax.set_ylabel("Puntaje promedio acumulado")
    ax.set_title("Estabilización del puntaje medio por partida (LGN)")
    ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "fig4_puntajes.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- Experimento 3
def experiment_winrate(n_games, seed, out_dir):
    print("\n=== Experimento 3: tasa de victorias (empate = 0.5) ===")
    matchups = [("Heurística", "Aleatoria"), ("Voraz", "Aleatoria"), ("Heurística", "Voraz")]
    fig, ax = plt.subplots(figsize=(8, 5))
    rows = []
    for k, (a, b) in enumerate(matchups):
        rng = random.Random(seed + 100 + k)
        wins = []
        for g in range(n_games):
            pa, pb = Player(a, _build(a, rng)), Player(b, _build(b, rng))
            if g % 2:                                  # alterna quién abre
                pa, pb = pb, pa
            res = Game([pa, pb], rng).play()
            t = res["totals"]
            wins.append(0.5 if t[a] == t[b] else float(t[a] > t[b]))
        arr = np.array(wins)
        running = np.cumsum(arr) / np.arange(1, n_games + 1)
        rate = arr.mean(); ci = 1.96 * arr.std(ddof=1) / math.sqrt(n_games)
        rows.append((f"{a} vs {b}", n_games, rate, ci))
        ax.semilogx(np.arange(1, n_games + 1), running, lw=1.4, label=f"{a} vs {b} ({100 * rate:.1f}%)")
    for name, n, rate, ci in rows:
        print(f"{name:<24} | n={n:>6} | gana {100 * rate:>6.2f}% ± {100 * ci:.2f}%")
    with open(os.path.join(out_dir, "exp3_victorias.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["enfrentamiento", "n", "tasa_victoria_primero", "ic95_mitad"])
        w.writerows(rows)
    ax.axhline(0.5, color="gray", ls=":")
    ax.set_xlabel("Número de partidas"); ax.set_ylabel("Tasa de victoria acumulada del primer jugador")
    ax.set_title("Convergencia de la tasa de victorias"); ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, "fig5_victorias.png"), dpi=150); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description="Simulación Montecarlo de Yahtzee")
    ap.add_argument("--rolls-exp", type=int, default=6, help="N máximo de lanzamientos = 10^exp")
    ap.add_argument("--games", type=int, default=5000, help="partidas por experimento")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "figures"))
    args = ap.parse_args()

    experiment_single_roll(args.rolls_exp, args.seed, args.out)
    experiment_scores(args.games, args.seed, args.out)
    experiment_winrate(args.games, args.seed, args.out)
    print(f"\nFiguras y CSV guardados en: {args.out}")


if __name__ == "__main__":
    main()
