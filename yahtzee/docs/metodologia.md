# Metodología: USA → MODIFICA → CREA

No se recibió una guía base, por lo que la etapa USA parte de un prototipo mínimo
construido con las reglas oficiales del juego.

## 1. USA  (`base/yahtzee_base.py`)
Se ejecuta tal cual un prototipo de ~20 líneas: lanzar 5 dados, relanzar al azar
dos veces y puntuar solo "Yahtzee". Se observa su comportamiento y se identifican
sus límites: un solo jugador, una sola categoría, relanzamiento aleatorio (sin
decisión), sin pruebas, sin forma de repetir experimentos.

## 2. MODIFICA  (`src/`)
- Se separa en módulos: dados, puntaje, jugador, estrategias, juego, interfaz.
- Se implementan las 13 categorías y el bono superior.
- Se agregan 2 jugadores, 13 turnos, máximo 3 lanzamientos y elección de qué dados conservar.
- Se agrega semilla aleatoria para reproducibilidad.
- Se agregan pruebas unitarias con `pytest`.

## 3. CREA  (`strategies.py`, `simulation/`)
- Jugadores automáticos: Aleatoria (línea base), Voraz y Heurística.
- Interfaz de consola con humano o bots.
- Montecarlo con tres experimentos:
  1. Frecuencia relativa de eventos en un lanzamiento vs N (10²…10⁶) y comparación con la probabilidad teórica.
  2. Puntaje medio por partida de cada estrategia vs número de partidas, con IC 95 %.
  3. Tasa de victorias entre estrategias vs número de partidas.

## Validación
- `test_conteo_exhaustivo_coincide_con_teoria` enumera los 7776 resultados y confirma
  6 (Yahtzee), 240 (escalera larga), 300 (full house) y 150 (póker exacto).
- Se verifica que el error absoluto decrece aproximadamente como √(p(1-p)/N) (`fig2_error.png`).

## Decisiones de alcance
No se implementan el bono de Yahtzee extra (+100) ni las reglas de comodín (Joker);
quedan como trabajo futuro.
