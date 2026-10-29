import pandas as pd
from tabulate import tabulate
import numpy as np
import time

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
    (coords_y[:, None] - coords_y[None, :]) ** 2)

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
    - OPÇÃO B: Abrir uma nova rota a partir de qualquer um dos 4 depósitos operacionais.
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

distancia_neh_puro  = calcular_distancia_final(todas_rotas, df_nos)

# Dicionário de demandas dos clientes para consulta rápida
demandas = dict(zip(df_nos["N_ID"], df_nos["Demanda"]))

def executar_swap(todas_rotas, cargas_rotas, capacidade_maxima=10, verbose=True):
    """
    Troca clientes entre rotas diferentes (1 <-> 1) se houver redução de km.
    Para cada cliente, encontra o melhor parceiro de troca viável.
    """
    melhorou_global = False
    for r1_idx in range(len(todas_rotas)):
        rota1 = todas_rotas[r1_idx]
        i = 1
        while i < len(rota1) - 1:
            c1 = rota1[i]
            cid1 = int(c1.split("_")[-1])
            dem1 = demandas[cid1]

            melhor_delta = -1e-4
            melhor_r2_idx = None
            melhor_j = None

            for r2_idx in range(len(todas_rotas)):
                if r2_idx == r1_idx:
                    continue
                rota2 = todas_rotas[r2_idx]
                carga1 = cargas_rotas[r1_idx]
                carga2 = cargas_rotas[r2_idx]

                for j in range(1, len(rota2) - 1):
                    c2 = rota2[j]
                    cid2 = int(c2.split("_")[-1])
                    dem2 = demandas[cid2]

                    # 1 - Validação estrita de capacidade
                    nova_carga1 = carga1 - dem1 + dem2
                    nova_carga2 = carga2 - dem2 + dem1
                    if nova_carga1 > capacidade_maxima or nova_carga2 > capacidade_maxima:
                        continue

                    # 2 - Saldo delta de quilometragem da troca
                    delta = ((obter_distancia(rota1[i - 1], c2) + obter_distancia(c2, rota1[i + 1])
                             - obter_distancia(rota1[i - 1], c1) - obter_distancia(c1, rota1[i + 1]))
                           + (obter_distancia(rota2[j - 1], c1) + obter_distancia(c1, rota2[j + 1])
                             - obter_distancia(rota2[j - 1], c2) - obter_distancia(c2, rota2[j + 1])))

                    if delta < melhor_delta:
                        melhor_delta = delta
                        melhor_r2_idx = r2_idx
                        melhor_j = j

            # 3 - Efetiva a melhor troca encontrada para o cliente
            if melhor_r2_idx is not None:
                c2_nome = todas_rotas[melhor_r2_idx][melhor_j]
                cid2 = int(c2_nome.split("_")[-1])
                dem2 = demandas[cid2]

                if verbose:
                    print(f"[SWAP] Rota {r1_idx + 1:2d} ({c1}) <-> Rota {melhor_r2_idx + 1:2d} ({c2_nome}) | Economia: {abs(melhor_delta):6.2f} km")

                rota1[i], todas_rotas[melhor_r2_idx][melhor_j] = c2_nome, c1
                cargas_rotas[r1_idx] = cargas_rotas[r1_idx] - dem1 + dem2
                cargas_rotas[melhor_r2_idx] = cargas_rotas[melhor_r2_idx] - dem2 + dem1
                melhorou_global = True
            i += 1
    return melhorou_global

def executar_reallocation(todas_rotas, cargas_rotas, capacidade_maxima=10, verbose=True):
    """
    Move um cliente de uma rota para outra (1 -> 0), podendo extinguir rotas vazias.
    Para cada cliente, encontra a melhor posição de realocação viável.
    """
    melhorou_global = False
    for r_idx in range(len(todas_rotas)):
        rota = todas_rotas[r_idx]
        i = 1
        while i < len(rota) - 1:
            c = rota[i]
            cid = int(c.split("_")[-1])
            dem = demandas[cid]

            # Ganho obtido ao remover o cliente da rota atual
            ganho_remocao = (obter_distancia(rota[i - 1], c) + obter_distancia(c, rota[i + 1])
                            - obter_distancia(rota[i - 1], rota[i + 1]))

            melhor_delta_total = -1e-4
            melhor_r2_idx = None
            melhor_pos = None

            for r2_idx in range(len(todas_rotas)):
                if r2_idx == r_idx:
                    # Avalia outras posições na mesma rota
                    rota_sem = rota[:i] + rota[i + 1:]
                    for pos in range(1, len(rota_sem)):
                        if pos == i:
                            continue
                        custo_insercao = (obter_distancia(rota_sem[pos - 1], c) + obter_distancia(c, rota_sem[pos])
                                         - obter_distancia(rota_sem[pos - 1], rota_sem[pos]))
                        delta_total = custo_insercao - ganho_remocao
                        if delta_total < melhor_delta_total:
                            melhor_delta_total = delta_total
                            melhor_r2_idx = r2_idx
                            melhor_pos = pos
                else:
                    if cargas_rotas[r2_idx] + dem > capacidade_maxima:
                        continue
                    rota2 = todas_rotas[r2_idx]
                    for pos in range(1, len(rota2)):
                        custo_insercao = (obter_distancia(rota2[pos - 1], c) + obter_distancia(c, rota2[pos])
                                         - obter_distancia(rota2[pos - 1], rota2[pos]))
                        delta_total = custo_insercao - ganho_remocao
                        if delta_total < melhor_delta_total:
                            melhor_delta_total = delta_total
                            melhor_r2_idx = r2_idx
                            melhor_pos = pos

            # Efetiva a realocação se houver redução de km
            if melhor_r2_idx is not None:
                if verbose:
                    print(f"[REALLOC] Moveu {c} de Rota {r_idx + 1:2d} -> Rota {melhor_r2_idx + 1:2d} (pos {melhor_pos}) | Economia: {abs(melhor_delta_total):6.2f} km")

                rota.pop(i)
                todas_rotas[melhor_r2_idx].insert(melhor_pos, c)
                cargas_rotas[r_idx] -= dem
                cargas_rotas[melhor_r2_idx] += dem
                melhorou_global = True
            else:
                i += 1

    # Elimina rotas esvaziadas (com apenas [Depósito, Porto Seco])
    indices_validos = [k for k, r in enumerate(todas_rotas) if len(r) > 2]
    if len(indices_validos) < len(todas_rotas):
        rotas_eliminadas = len(todas_rotas) - len(indices_validos)
        if verbose:
            print(f"[REALLOC] {rotas_eliminadas} rota(s) esvaziada(s) e eliminada(s) com sucesso!")
        todas_rotas[:] = [todas_rotas[k] for k in indices_validos]
        cargas_rotas[:] = [cargas_rotas[k] for k in indices_validos]

    return melhorou_global


def executar_2opt(todas_rotas, verbose=True):
    """
    Desfaz cruzamentos intra-rota invertendo subsequências de clientes.
    """
    melhorou_global = False
    for r_idx, rota in enumerate(todas_rotas):
        melhorou_rota = True
        while melhorou_rota:
            melhorou_rota = False
            n = len(rota)
            for i in range(1, n - 2):
                for j in range(i + 1, n - 1):
                    delta = (obter_distancia(rota[i - 1], rota[j]) + obter_distancia(rota[i], rota[j + 1])
                            - obter_distancia(rota[i - 1], rota[i]) - obter_distancia(rota[j], rota[j + 1]))

                    if delta < -1e-4:
                        if verbose:
                            print(f"[2-OPT] Rota {r_idx + 1:2d}: Inverteu {rota[i]} até {rota[j]} | Economia: {abs(delta):6.2f} km")
                        rota[i:j + 1] = rota[i:j + 1][::-1]
                        melhorou_rota = True
                        melhorou_global = True
                        break
                if melhorou_rota:
                    break
    return melhorou_global

# Execução do Ciclo Exaustivo de Busca Local com Rastreamento Completo
print("Iniciando busca local (Swap -> Reallocation -> 2-Opt)")

tempo = time.perf_counter()
iteracao = 0
verbose = False

while True:
    iteracao += 1
    print(f"\nPassada {iteracao}")

    print("[1/3] Executando Swap...")
    m_swap = executar_swap(todas_rotas, cargas_rotas, capacidade_veiculo, verbose=False)

    print("[2/3] Executando Reallocation...")
    m_realloc = executar_reallocation(todas_rotas, cargas_rotas, capacidade_veiculo, verbose=False)

    print("[3/3] Executando 2-Opt...")
    m_2opt = executar_2opt(todas_rotas, verbose=False)

    # Distância total acumulada calculada diretamente via obter_distancia
    dist_parcial = sum(sum(obter_distancia(r[k], r[k + 1]) for k in range(len(r) - 1)) for r in todas_rotas)
    print(f"\nRESUMO DA PASSADA {iteracao}:")
    print(f"Swap: {str(m_swap):5s} | Realloc: {str(m_realloc):5s} | 2-Opt: {str(m_2opt):5s}")
    print(f"Distância Global Atual: {dist_parcial:10.2f} km | Total de Rotas: {len(todas_rotas):2d}")

    if not m_swap and not m_realloc and not m_2opt:
        print("\nConvergência alcançada: Nenhum operador encontrou melhoria adicional!")
        break

tempo_bl = time.perf_counter() - tempo
print(f"\nTempo total de processamento da busca local: {tempo_bl:.4f} segundos")

# Exibição das rotas finais e confronto de desempenho
distancia_final = calcular_distancia_final(todas_rotas, df_nos)

economia_km = distancia_neh_puro - distancia_final
economia_pct = (economia_km / distancia_neh_puro) * 100

print("NEH PURO vs NEH COM BUSCA LOCAL")
print(f"Distância Inicial (NEH Puro):           {distancia_neh_puro:>10,.2f} km")
print(f"Distância Final (NEH com Busca Local):  {distancia_final:>10,.2f} km")
print(f"Economia Absoluta Gerada:               {economia_km:>10,.2f} km")
print(f"Melhoria Percentual:                    {economia_pct:>10.2f} %")
