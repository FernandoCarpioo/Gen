#Carpio Monjaraz Fernando Aldair
# Rivera Martinez Cristhian Antonio


import random

LOG_FILE = "registro.txt"

NUM_FEATURES = 20
LOWER = 1
UPPER = 9
POPULATION_SIZE = 100

def create_initial_population(size, num_features, lower, upper):
    population = []
    for i in range(size):  
        individual = ([random.randint(lower, upper) for _ in range(num_features)], i+1, 0)
        population.append(individual)
    return population

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

def son_familiares(ind1, ind2, genealogia):
    # ID'S
    padres1 = genealogia.get(ind1[1], [])
    padres2 = genealogia.get(ind2[1], [])
    
    # Hermanos
    if set(padres1) == set(padres2) and padres1:
        return True
    
    # Primos
    for p1 in padres1:
        for p2 in padres2:
            abuelos_p1 = genealogia.get(p1, [])
            abuelos_p2 = genealogia.get(p2, [])
            if set(abuelos_p1) == set(abuelos_p2) and abuelos_p1:
                return True
    return False

# Selección aleatoria
def formar_parejas(population, genealogia):
    parejas = []
    usados = set()
    disponibles = list(range(len(population)))
    random.shuffle(disponibles)
    
    for i in disponibles:
        if i in usados:
            continue
            
        for j in disponibles:
            if j in usados or i == j:
                continue
                
            if not son_familiares(population[i], population[j], genealogia):
                parejas.append((population[i], population[j]))
                usados.add(i)
                usados.add(j)
                break
        
        if len(parejas) >= 50:
            break
    
    return parejas

def mutar(individuo, prob=0.0001, max_mutaciones=2):
    # Mutar cada característica
    individuo_mutado = individuo.copy()
    mutaciones= 0
    muto_gen= False
    genes_mutados =[]

    for i in range(len(individuo_mutado)):
        if mutaciones >= max_mutaciones: #Con esto aseguramos que solamente dos o menos genes por individuo mutaron
            break
        if random.random() < prob:
            individuo_mutado[i] = random.randint(9, UPPER)
            mutaciones += 1
            muto_gen = True #Con esto detectamos si un gen muto, para nuestro reporte

    return individuo_mutado, muto_gen

def registrar_individuo(generacion, individuo_id, genes, mutado):
    with open (LOG_FILE, "a") as f:
        f.write(f"Generacion {generacion}, ID {individuo_id}, Genes{genes}, Mutacion{'Si'if mutado else 'No'}\n")

def es_perfecto(individuo):
    return all(g == UPPER for g in individuo)

def main():

    open(LOG_FILE, "w").close()

    population = create_initial_population(POPULATION_SIZE, NUM_FEATURES, LOWER, UPPER)
    genealogia = {ind[1]: [] for ind in population}
    
    print("Población inicial (primeros 3 individuos):")
    for i in range(3):
        print(f"Individuo {i+1}: {population[i]}")
    
    generacion = 1
    encontrado = False
    individuo_perfecto = None
    
    while not encontrado and generacion <= 1000:
        parejas = formar_parejas(population, genealogia)
        nueva_poblacion = []
        nuevo_genealogia = {}
        siguiente_id = max(ind[1] for ind in population) + 1
        
        for padre1, padre2 in parejas:
            # Reproducir
            hijo1_genes, hijo2_genes = reproducir(padre1[0], padre2[0])
            
            # Mutar solo el segundo hijo
            hijo2_genes, mutado = mutar(hijo2_genes, prob=0.04)
            
            # Crear nuevos individuos
            hijo1 = (hijo1_genes, siguiente_id, generacion)
            hijo2 = (hijo2_genes, siguiente_id + 1, generacion)

            registrar_individuo(generacion, siguiente_id, hijo1_genes, False)
            registrar_individuo(generacion, siguiente_id + 1, hijo2_genes, mutado)
            
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
        
        # Actualizar para la siguiente generación
        population = nueva_poblacion
        genealogia.update(nuevo_genealogia)
        
        # Mostrar progreso cada 25 generaciones
        if generacion % 25 == 0:
            mejor = max(population, key=lambda ind: ind[0].count(UPPER))
            print(f"Generación {generacion}: Mejor individuo tiene {mejor[0].count(UPPER)}/{NUM_FEATURES} genes en 9")
        
        generacion += 1
    
    print("\n" + "=-"*40)
    if encontrado:
        print(f"¡INDIVIDUO PERFECTO ENCONTRADO EN LA GENERACIÓN {generacion-1}!")
        print(f"ID: {individuo_perfecto[1]}")
        print(f"Genes: {individuo_perfecto[0]}")
        # print(f"Todos los genes son {UPPER}: {es_perfecto(individuo_perfecto[0])}")
    else:
        mejor = max(population, key=lambda ind: ind[0].count(UPPER))
        print(f"Mejor individuo encontrado (no perfecto) después de {generacion-1} generaciones:")
        print(f"ID: {mejor[1]}")
        print(f"Genes: {mejor[0]}")
        print(f"Genes en {UPPER}: {mejor[0].count(UPPER)}/{NUM_FEATURES}")

if __name__ == "__main__":
    main()