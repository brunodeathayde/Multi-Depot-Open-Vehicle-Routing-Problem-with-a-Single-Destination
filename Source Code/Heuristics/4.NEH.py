import pandas as pd
from tabulate import tabulate
import numpy as np

instancia = "I_100_4_1.xlsx"

df_nos = pd.read_excel(instancia, sheet_name="Nos")
df_frota = pd.read_excel(instancia, sheet_name="Frota")

# Função para calcular a distância euclidiana entre dois pontos
def calcular_distancia(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Pré-cálculo da matriz de distâncias euclidianas
coords_x = df_nos["X"].to_numpy()
coords_y = df_nos["Y"].to_numpy()
dist_matrix = np.sqrt(
    (coords_x[:, None] - coords_x[None, :]) ** 2 +
    (coords_y[:, None] - coords_y[None, :]) ** 2
)

def obter_distancia(id_a, id_b):
    # Extrai o número se for texto ("D_1", "P_105", "C_10") ou se já for número
    a = int(str(id_a).split("_")[-1].split("(")[0])
    b = int(str(id_b).split("_")[-1].split("(")[0])
    return dist_matrix[a - 1, b - 1]

def calcular_delta(id_anterior, id_cliente, id_proximo):
    """
    Calcula o acréscimo de quilometragem (desvio) ao colocar o cliente entre dois pontos:
    Delta = dist(anterior -> cliente) + dist(cliente -> proximo) - dist(anterior -> proximo)
    """
    dist_chegando = obter_distancia(id_anterior, id_cliente)
    dist_saindo   = obter_distancia(id_cliente, id_proximo)
    dist_original = obter_distancia(id_anterior, id_proximo)

    delta = dist_chegando + dist_saindo - dist_original
    return delta

def avaliacao(cliente_id, demanda_cliente, todas_rotas, cargas_rotas, verbose=False):
    """
    Avalia todas as possibilidades de atendimento:
    - OPÇÃO A: Inserir em alguma rota já aberta com capacidade residual livre;
    - OPÇÃO B: Abrir uma nova rota a partir de qualquer um dos depósitos operacionais.
    Retorna a ação com o menor acréscimo de distância (Delta km).
    """
    melhor_delta = float("inf")
    melhor_acao = None
    porto = f"P_{porto_id}"
    cliente_str = f"C_{cliente_id}"

    # OPÇÃO A: Testar inserção em todas as posições de todas as rotas abertas
    if verbose: print(f"\n[Opção A] Testando {len(todas_rotas)} rotas abertas")
    for r_idx, rota in enumerate(todas_rotas):

        livre = capacidade_veiculo - cargas_rotas[r_idx]

        # Validação estrita de capacidade (Q <= 10 t)
        if demanda_cliente > livre:
            
            if verbose: print(f"✘ Rota {r_idx + 1:2d} sem espaço ({cargas_rotas[r_idx]:.1f}t/{capacidade_veiculo:.0f}t | livre: {livre:.1f}t). Pulando...")
            continue

        for pos in range(1, len(rota)):
            no_ant = rota[pos - 1]
            no_prox = rota[pos]

            delta = calcular_delta(no_ant, cliente_str, no_prox)

            if verbose: print(f"➜ Rota {r_idx + 1:2d} (entre {no_ant} e {no_prox}): Delta = {delta:6.2f} km")

            if delta < melhor_delta:
                melhor_delta = delta
                melhor_acao = ("inserir", r_idx, pos, delta)

    # OPÇÃO B: Testar abertura de nova rota a partir de cada um dos depósitos
    if verbose: print(f"\n[Opção B] Testando criar nova rota a partir dos depósitos")
    for dep_id in depositos["N_ID"]:
        custo_novo = obter_distancia(f"D_{dep_id}", cliente_str) + obter_distancia(cliente_str, porto)

        if verbose: print(f"[★] Novo caminhão saindo de D_{dep_id}: Custo = {custo_novo:6.2f} km")
        
        if custo_novo < melhor_delta:
            melhor_delta = custo_novo
            melhor_acao = ("nova_rota", int(dep_id), None, custo_novo)
            
    return melhor_acao

# Função para calcular a distância total de cada rota e a distância global
def calcular_distancia_final(todas_rotas, df_nos):
    distancia_total = 0

    # Loop para cada uma das rotas geradas
    for i, rota in enumerate(todas_rotas, start=1):
        distancia_rota = 0
 
        for j in range(len(rota)-1):
            distancia_rota += obter_distancia(rota[j], rota[j+1])

        print(
            f"Rota {i:<3} | "
            f"({len(rota)-2:>2} clientes) |"
            f"{distancia_rota:>10,.2f} km | "
            f"{' -> '.join(todas_rotas[i-1])}")
        
        distancia_total += distancia_rota

    print(f"Distancia total de todas as rotas: {distancia_total:,.2f} km")

    return distancia_total

# Filtro da tabela para obter apenas os clientes (Tipo == 'C')
clientes = df_nos[df_nos['Tipo'] == 'C'].sort_values(["Demanda","N_ID"], ascending=[False, True])
print(f"{tabulate(clientes.head(), headers="keys", tablefmt="fancy_grid")}\n")

# Filtro da tabela para obter apenas os depósitos (Tipo == 'D')
depositos = df_nos[df_nos["Tipo"] == "D"]
print(f"{tabulate(depositos, headers="keys", tablefmt="fancy_grid")}\n")

# Identificação do Porto Seco (Tipo == 'P')
porto = df_nos[df_nos["Tipo"] == "P"].index[0]
porto_id = df_nos.loc[porto, "N_ID"]
print(f"Porto Seco ID: {porto_id}")

clientes_restantes = clientes.copy()
capacidade_veiculo = 10
todas_rotas = []
cargas_rotas = []
verbose = False

while not clientes_restantes.empty:
    # 1 - Pega o cliente do topo (maior demanda restante)
    index_cliente = clientes_restantes.index[0]
    cliente_id = clientes_restantes.loc[index_cliente,"N_ID"]
    demanda = clientes_restantes.loc[index_cliente, "Demanda"]

    # 2 - Chama a função avaliar 
    melhor_acao = avaliacao(cliente_id,demanda,todas_rotas,cargas_rotas)

    tipo_acao, alvo, pos, delta = melhor_acao

    # 3 - Aplica a decisão
    if tipo_acao == "nova_rota":
        nova_rota = [f"D_{alvo}", f"C_{cliente_id}", f"P_{porto_id}",]
        todas_rotas.append(nova_rota)
        cargas_rotas.append(demanda)
        if verbose: print(f"[+] Cliente {cliente_id:2d} -> Nova Rota {len(todas_rotas):2d} (D_{alvo}) | Coletou {demanda:5.2f}t")
    else:
        todas_rotas[alvo].insert(pos, f"C_{cliente_id}")
        cargas_rotas[alvo] += demanda
        if verbose: print(f"[+] Cliente {cliente_id:2d} -> Inserido Rota {alvo + 1:2d} (pos {pos}) | Coletou {demanda:5.2f}t")

     # 4 - Remove o cliente atendido da lista
    clientes_restantes = clientes_restantes.drop(index_cliente)
    
print(f"\nTotal de rotas geradas: {len(todas_rotas)}")

distancia_final = calcular_distancia_final(todas_rotas, df_nos)