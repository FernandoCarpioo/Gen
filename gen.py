import random


def crear_persona():
    return [random.randint(1,9) for _ in range(20)]

def crear_poblacion(n=100):
    return [crear_persona() for _ in range (n)]

def reproducir(padre1, padre2):
    hijo1, hijo2 = [], []
    for g1, g2 in zip(padre1, padre2):
        promedio = (g1 + g2) /2
        if promedio.is_integer():
            valor = int(promedio)
        else:
            valor = int(promedio) + (1 if random.random()< 0.5 else 0)
        hijo1.append(valor)
        hijo2.append(valor)
    return hijo1, hijo2