import pandas as pd
from tabulate import tabulate
import numpy as np
import random

instancia = "I_100_4_1.xlsx"

df_nos = pd.read_excel(instancia, sheet_name="Nos")
df_frota = pd.read_excel(instancia, sheet_name="Frota")

# Função para calcular a distância euclidiana entre dois pontos
def calcular_distancia(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Função para calcular a distância total de cada rota e a distância global
def calcular_distancia_final(todas_rotas, df_nos):
    distancia_total = 0

    # Loop para cada uma das rotas geradas
    for i, rota in enumerate(todas_rotas, start=1):
        distancia_rota = 0
 
        for j in range(len(rota)-1):

            id_a = int(str(rota[j]).split("_")[-1])
            id_b = int(str(rota[j+1]).split("_")[-1])

            xa, ya = df_nos.loc[id_a-1, ["X","Y"]]
            xb, yb = df_nos.loc[id_b-1, ["X","Y"]]

            distancia_rota += calcular_distancia(xa, ya, xb, yb)

        print(
            f"Rota {i:<3} | "
            f"({len(rota)-2:>2} clientes) |"
            f"{distancia_rota:>10,.2f} km | "
            f"{" -> ".join(todas_rotas[i-1])}")
        
        distancia_total += distancia_rota

    print(f"Distancia total de todas as rotas: {distancia_total:,.2f} km")

    return distancia_total

# Filtro da tabela para obter apenas os clientes (Tipo == 'C')
clientes = df_nos[df_nos['Tipo'] == 'C']
print(f"{tabulate(clientes.head(), headers="keys", tablefmt="fancy_grid")}\n")

# Filtro da tabela para obter apenas os depósitos (Tipo == 'D')
depositos = df_nos[df_nos["Tipo"] == "D"]
print(f"{tabulate(depositos, headers="keys", tablefmt="fancy_grid")}\n")

# Identificação do Porto Seco (Tipo == 'P')
porto = df_nos[df_nos["Tipo"] == "P"].index[0]
porto_id = df_nos.loc[porto, "N_ID"]
print(f"Porto Seco ID: {porto_id}")

clientes_restantes = clientes.copy()
todas_rotas = []
indice_veiculo = 0
todos_depositos = depositos["N_ID"].tolist()
random.seed(42)  # Garante reprodutibilidade

# Loop principal: roda até que todos os clientes sejam atendidos
while not clientes_restantes.empty:

    # 1 - Pega o veículo da aba Frota (ou gera Extra se a frota inicial acabar)
    if indice_veiculo < len(df_frota):
        linha_frota = df_frota.iloc[indice_veiculo]
        deposito_id = linha_frota["Deposito_ID"]
        capacidade_atual = linha_frota["Capacidade"]
    else:
        deposito_id = random.choice(todos_depositos)
        capacidade_atual = 10

    # 2 - Ponto de partida: o depósito onde o caminhão está alocado
    x_dep, y_dep = depositos.loc[depositos["N_ID"] == deposito_id, ["X", "Y"]].values[0]
    x_atual, y_atual = x_dep, y_dep
    rota_atual = [f"D_{deposito_id}"]

    # 3 - Loop de coleta: busca o vizinho mais próximo enquanto couber no caminhão
    while True:
        clientes_validos = clientes_restantes[clientes_restantes["Demanda"] <= capacidade_atual]

        if clientes_validos.empty:
            break

        menor_distancia = float("inf")
        melhor_index = None
        melhor_id = None
        melhor_demanda = None
        melhor_x, melhor_y = None, None

        for index, linha in clientes_validos.iterrows():
            distancia = calcular_distancia(x_atual, y_atual, linha["X"], linha["Y"])
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_index = index
                melhor_id = linha["N_ID"]
                melhor_demanda = linha["Demanda"]
                melhor_x, melhor_y = linha["X"], linha["Y"]

        # Insere o cliente na rota, reduz capacidade e atualiza posição
        rota_atual.append(f"C_{melhor_id}")
        capacidade_atual -= melhor_demanda
        x_atual, y_atual = melhor_x, melhor_y
        clientes_restantes = clientes_restantes.drop(melhor_index)

    # 4 - Fecha a rota no Porto Seco se o caminhão atendeu clientes
    rota_atual.append(f"P_{porto_id}")
    todas_rotas.append(rota_atual)
    indice_veiculo += 1

distancia_final = calcular_distancia_final(todas_rotas, df_nos)