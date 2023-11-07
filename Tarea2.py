import pulp
import math

# Abre el archivo de instancia de TSPLIB95
with open("br17.atsp") as f:
    lines = f.readlines()

# Encuentra la línea que inicia la sección EDGE_WEIGHT_SECTION
start_index = lines.index("EDGE_WEIGHT_SECTION\n") + 1

# Encuentra la línea que marca el final de la sección
end_index = lines.index("EOF\n")

# Extrae las líneas que contienen los valores de la matriz de costos
cost_lines = lines[start_index:end_index]
cost_data = "".join(cost_lines)
cost_values = cost_data.split()
num_cities = int(math.sqrt(len(cost_values)))

# Divide los valores en filas y columnas y almacénalos como una lista de listas de enteros
aux = 0
c = []
for i in range(num_cities):
    fila = []
    for j in range(num_cities):
        fila.append(int(cost_values[aux]))
        aux += 1
    c.append(fila)

# Crea un problema de minimización
problem = pulp.LpProblem("ATSP_DFJ", pulp.LpMinimize)

# Variables binarias: x[i][j] = 1 si se va de la ciudad i a la ciudad j
x = [[pulp.LpVariable(f'x_{i}_{j}', cat=pulp.LpBinary) for j in range(num_cities)] for i in range(num_cities)]

# Función objetivo: minimizar la distancia total
problem += pulp.lpSum(x[i][j] * c[i][j] for i in range(num_cities) for j in range(num_cities))

# Restricción 1: De cada ciudad sale exactamente una arista
for i in range(num_cities):
    problem += pulp.lpSum(x[i][j] for j in range(num_cities)) == 1

# Restricción 2: A cada ciudad llega exactamente una arista
for j in range(num_cities):
    problem += pulp.lpSum(x[i][j] for i in range(num_cities)) == 1

# Restricción 3: Evitar subciclos
u = [pulp.LpVariable(f'u_{i}', lowBound=0, cat=pulp.LpInteger) for i in range(num_cities)]
for i in range(1, num_cities):
    for j in range(1, num_cities):
        if i != j:
            problem += u[i] - u[j] + (num_cities - 1) * x[i][j] <= num_cities - 2

# Resuelve el problema
problem.solve(pulp.PULP_CBC_CMD(timeLimit=1800))

# Imprime la solución
if pulp.LpStatus[problem.status] == "Optimal":
    print("Solución óptima encontrada:")
    tour = [0]
    i = 0
    while True:
        for j in range(num_cities):
            if i != j and pulp.value(x[i][j]) == 1:
                tour.append(j)
                i = j
                break
        if i == 0:
            break
    print("Camino óptimo:", tour)
    print("Distancia total:", pulp.value(problem.objective))
else:
    print("No se encontró una solución óptima.")
