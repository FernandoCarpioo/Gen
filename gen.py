import random


def crar_persona():
    return [random.randint(1,9) for _ in range(20)]

def crar_poblacion(n=100):
    return [crear_individuo() for _ in range (n)]

def reproducir(padre1, padre2):
    hijo1, hijo2 = [], []
    for g1, g2 in zip(padre1, padre2):
        promedio = (g1 + g2) /2
        if promedio.is_integerer():
            valor = int(promedio)