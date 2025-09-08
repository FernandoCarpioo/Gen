import numpy as np
import random

LOG_FILE = "genetica.txt"

NUM_FEATURES = 20
LOWER = 1
UPPER = 9
POPULATION_SIZE = 100

def create_initial_population(size, num_features, lower, upper):
    all_genes = np.where(
        np.random.random(size=(size, num_features)) < 0.1,
        np.random.randint(7, upper + 1, size=(size, num_features)),
        np.random.randint(lower, upper + 1, size=(size, num_features))
    )
    population = [
        (genes.tolist(), i + 1, 0)
        for i, genes in enumerate(all_genes)
    ]
    return population

    # population = []
    # for i in range(size):  
    #     individual = ([random.randint(lower, upper) for _ in range(num_features)], i+1, 0)
    #     population.append(individual)
    # return population


def reproducir(padre1, padre2):
    hijo1, hijo2 = [], []
    for g1, g2 in zip(padre1, padre2):
        promedio = (g1 + g2) / 2
        if promedio.is_integer():
            valor = int(promedio)
        else:
            # Redondeo siempre hacia arriba
            valor = int(promedio) + (0 if promedio.is_integer() else 1)
        hijo1.append(valor)
        hijo2.append(valor)
    return hijo1, hijo2

def obtener_ancestros(ind_id, genealogia, nivel):
    
    if nivel == 0 or ind_id not in genealogia:
        return set()
    
    ancestros = set()
    for padre_id in genealogia[ind_id]:
        ancestros.add(padre_id)
        ancestros |= obtener_ancestros(padre_id, genealogia, nivel - 1)
    
    return ancestros

def son_familiares(ind1, ind2, genealogia):
    id1, id2 = ind1[1], ind2[1]
    # Si son el mismo individuo
    if id1 == id2:
        return True
    
    # Obtener ancestros hasta, primos terceros
    ancestros1 = obtener_ancestros(id1, genealogia, 3)
    ancestros2 = obtener_ancestros(id2, genealogia, 3)
    
    # Si comparten algún ancestro en común, son familiares
    return len(ancestros1.intersection(ancestros2)) > 0

def seleccionar_mejores_padres(population, num_parejas):

    population_ordenada = sorted(population, key=lambda ind: (sum(ind[0]), ind[0].count(UPPER)), reverse=True)
    # Seleccionar los mejores para reproducirse
    mejores = population_ordenada[:num_parejas*2]
    parejas = []
    for i in range(0, len(mejores), 2):
        if i+1 < len(mejores):
            parejas.append((mejores[i], mejores[i+1]))
    
    return parejas

def formar_parejas(population, genealogia):
    num_parejas = len(population) // 2
    parejas = seleccionar_mejores_padres(population, num_parejas)
    
    # Verificar que no sean familiares
    parejas_no_familiares = []
    usados = set()
    
    for i, (ind1, ind2) in enumerate(parejas):
        idx1 = population.index(ind1)
        idx2 = population.index(ind2)
        if not son_familiares(ind1, ind2, genealogia) and idx1 not in usados and idx2 not in usados:
            parejas_no_familiares.append((ind1, ind2))
            usados.add(idx1)
            usados.add(idx2)

    if len(parejas_no_familiares) < num_parejas:
        disponibles = [i for i in range(len(population)) if i not in usados]
        
        for i in disponibles:
            if i in usados:
                continue
            for j in disponibles:
                if j in usados or i == j:
                    continue
                if not son_familiares(population[i], population[j], genealogia):
                    parejas_no_familiares.append((population[i], population[j]))
                    usados.add(i)
                    usados.add(j)
                    break
    return parejas_no_familiares

def mutar(individuo, prob=0.01, max_mutaciones=2):
    individuo_mutado = individuo.copy()
    mutaciones= 0
    muto_gen= False
    genes_mutados =[]

    for i in range(len(individuo_mutado)):
        #Con esto aseguramos que solamente dos o menos genes por individuo mutaron
        if mutaciones >= max_mutaciones: 
            break
        if random.random() < prob:
            individuo_mutado[i] = random.randint(UPPER, UPPER)
            mutaciones += 1
            #Con esto detectamos si un gen muto
            muto_gen = True 

    return individuo_mutado, muto_gen

def registrar_mejor_individuo(generacion, mejor_individuo):
    suma = np.sum(mejor_individuo[0])
    with open(LOG_FILE, "a") as f:
        f.write(f"Generacion {generacion}, ID: {mejor_individuo[1]}, Genes: {mejor_individuo[0]}, Suma: {suma}\n")

def es_perfecto(individuo):
    return all(g == UPPER for g in individuo)

def main():
    open(LOG_FILE, "w").close()
    population = create_initial_population(POPULATION_SIZE, NUM_FEATURES, LOWER, UPPER)
    genealogia = {ind[1]: [] for ind in population}
    generacion = 0
    encontrado = False
    individuo_perfecto = None
    
    while not encontrado and generacion <= 50:
        parejas = formar_parejas(population, genealogia)
        nueva_poblacion = []
        nuevo_genealogia = {}
        siguiente_id = max([ind[1] for ind in population]) + 1 if population else 1
        
        for padre1, padre2 in parejas:
            # Reproducir
            hijo1_genes, hijo2_genes = reproducir(padre1[0], padre2[0])
            # Mutar solo el segundo hijo
            hijo2_genes, mutado = mutar(hijo2_genes, prob=0.01)
            # Crear nuevos individuos
            hijo1 = (hijo1_genes, siguiente_id, generacion)
            hijo2 = (hijo2_genes, siguiente_id + 1, generacion)
            # Actualizar genealogía
            nuevo_genealogia[siguiente_id] = [padre1[1], padre2[1]]
            nuevo_genealogia[siguiente_id + 1] = [padre1[1], padre2[1]]
            nueva_poblacion.extend([hijo1, hijo2])
            siguiente_id += 2
            
            # Verificar si encontramos el individuo perfecto
            if es_perfecto(hijo1_genes):
                encontrado = True
                individuo_perfecto = hijo1
                break
            elif es_perfecto(hijo2_genes):
                encontrado = True
                individuo_perfecto = hijo2
                break
        
        # Encontrar el mejor individuo de la generación
        if nueva_poblacion:
            mejor_individuo = max(nueva_poblacion, key=lambda ind: (sum(ind[0]), ind[0].count(UPPER)))
            registrar_mejor_individuo(generacion, mejor_individuo)

        
        # Actualizar para la siguiente generación
        population = nueva_poblacion
        genealogia.update(nuevo_genealogia)
        generacion += 1
    
    print("\n" + "=-"*40)
    if encontrado:
        print(f"¡INDIVIDUO PERFECTO ENCONTRADO EN LA GENERACIÓN {generacion-1}!")
        print(f"ID: {individuo_perfecto[1]}")
        print(f"Genes: {individuo_perfecto[0]}")

    else:
        mejor = max(population, key=lambda ind: ind[0].count(UPPER))
        print(f"Mejor individuo encontrado (no perfecto) después de {generacion-1} generaciones:")
        print(f"ID: {mejor[1]}")
        print(f"Genes: {mejor[0]}")
        print(f"Genes en {UPPER}: {mejor[0].count(UPPER)}/{NUM_FEATURES}")

if __name__ == "__main__":
    main()