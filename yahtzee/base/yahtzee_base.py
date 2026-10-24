"""
ETAPA "USA": prototipo base mínimo (un solo jugador, un solo turno).

Se toma tal cual la idea elemental del juego (lanzar 5 dados, relanzar al
azar hasta 2 veces y puntuar) SIN modificarla. Sirve como punto de partida
para la etapa MODIFICA, donde se reestructura todo en módulos.
"""
import random

def lanzar(n=5):
    return [random.randint(1, 6) for _ in range(n)]

def turno_basico():
    dados = lanzar()
    for _ in range(2):                      # hasta 2 relanzamientos
        dados = [d if random.random() < 0.5 else random.randint(1, 6) for d in dados]
    return dados

def puntaje_yahtzee(dados):
    return 50 if len(set(dados)) == 1 else 0

if __name__ == "__main__":
    dados = turno_basico()
    print("Dados:", dados, "| Puntos Yahtzee:", puntaje_yahtzee(dados))
