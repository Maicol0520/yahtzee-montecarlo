[README.md](https://github.com/user-attachments/files/33900934/README.md)
# Yahtzee 2 jugadores + simulación de Montecarlo

Simulación del Yahtzee clásico (5 dados, hasta 3 lanzamientos por turno, 13 categorías)
para 2 jugadores, con jugadores humanos o automáticos, y experimentos de Montecarlo
que ilustran la **Ley de los Grandes Números**.

## Instalación
```bash
pip install -r requirements.txt
```

## Uso
```bash
python src/cli.py                  # jugar (humano / bots)
python src/cli.py --seed 7         # partida reproducible
python simulation/montecarlo.py --rolls-exp 6 --games 5000 --seed 42
python -m pytest                   # pruebas
```
Los resultados del Montecarlo se guardan en `docs/figures/` (PNG y CSV).

## Estructura
| Ruta | Contenido |
|---|---|
| `base/yahtzee_base.py` | Etapa USA: prototipo mínimo inicial |
| `src/dice.py` | Lanzamiento y relanzamiento de dados |
| `src/scoring.py` | Puntaje de las 13 categorías |
| `src/player.py` | Tarjeta de puntajes y jugador |
| `src/strategies.py` | Estrategias: Aleatoria, Voraz, Heurística |
| `src/game.py` | Flujo de turnos y ganador |
| `src/cli.py` | Interfaz de consola |
| `simulation/montecarlo.py` | Experimentos de la LGN |
| `tests/` | Pruebas unitarias (incluye verificación exhaustiva de 6^5 resultados) |
| `docs/` | Metodología, resultados y figuras |

## Reglas implementadas
Bono superior de 35 pts si Unos–Seises suman ≥ 63. Full house 25, escalera corta 30,
escalera larga 40, Yahtzee 50. No se implementan el bono de Yahtzee extra (+100) ni los
comodines (decisión de alcance, ver `docs/metodologia.md`).
