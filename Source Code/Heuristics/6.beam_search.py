import pandas as pd
from tabulate import tabulate
import numpy as np
import time

instancia = "I_100_4_2.xlsx"

df_nos = pd.read_excel(instancia, sheet_name="Nos")
df_frota = pd.read_excel(instancia, sheet_name="Frota")

# Capacidade homogênea da frota
capacidade_veiculo = int(df_frota["Capacidade"].iloc[0])

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

# Função para calcular a distância total de cada rota e a distância global
def calcular_distancia_final(todas_rotas, df_nos):
    distancia_total = 0

    # Loop para cada uma das rotas geradas
    for i, rota in enumerate(todas_rotas, start=1):
        distancia_rota = 0

        # Percorre os pontos consecutivos da rota usando obter_distancia O(1)
        for j in range(len(rota)-1):
            distancia_rota += obter_distancia(rota[j], rota[j+1])

        # Exibe a distância individual da rota e soma na distância geral
        print(
            f"Rota {i:<3} | "
            f"({len(rota)-2:>2} clientes) |"
            f"{distancia_rota:>10,.2f} km | "
            f"{' -> '.join(rota)}")
        distancia_total += distancia_rota

    # Exibe a distância total acumulada de todas as rotas
    print(f"\nDistancia total de todas as rotas: {distancia_total:,.2f} km")

    return distancia_total

# Filtro da tabela para obter apenas os clientes (Tipo == 'C') ordenados por demanda decrescente
clientes = df_nos[df_nos['Tipo'] == 'C'].sort_values(by='Demanda', ascending=False)
print(f"{tabulate(clientes.head(), headers='keys', tablefmt='fancy_grid')}\n")

# Filtro da tabela para obter apenas os depósitos (Tipo == 'D')
depositos = df_nos[df_nos["Tipo"] == "D"]
print(f"{tabulate(depositos, headers='keys', tablefmt='fancy_grid')}\n")

# Identificação do Porto Seco (Tipo == 'P')
porto = df_nos[df_nos["Tipo"] == "P"].index[0]
porto_id = df_nos.loc[porto, "N_ID"]
print(f"Porto Seco ID: {porto_id}\n")

# Lista de visitas a partir dos clientes ordenados por demanda decrescente
visitas = [
    {
        "cliente_id": int(linha["N_ID"]),
        "demanda": float(linha["Demanda"]),
        "tipo": linha["Tipo"]
    }
    for _, linha in clientes.iterrows()
]

# Função de Expansão de uma Solução Parcial
def expandir_solucao(solucao_atual, visita, dep_ids, porto_id, capacidade_max, sol_idx=1):
    """
    Gera todas as extensões válidas para acomodar a visita na solução atual:
    - OPÇÃO A: Inserir a visita em rotas abertas onde a capacidade livre comportar a carga;
    - OPÇÃO B: Abrir uma nova rota a partir de qualquer um dos depósitos operacionais.
    """
    c_id = visita["cliente_id"]
    dem = visita["demanda"]
    c_str = f"C_{c_id}({dem:.2f}t)"
    
    rotas = solucao_atual["rotas"]
    cargas = solucao_atual["cargas"]
    custo_base = solucao_atual["custo"]
    novas_solucoes = []
    
    # OPÇÃO A: Inserir em rotas abertas com espaço livre
    for r_idx, rota in enumerate(rotas):
        if cargas[r_idx] + dem <= capacidade_max + 1e-6:
            for pos in range(1, len(rota)):
                no_ant = rota[pos - 1]
                no_prox = rota[pos]
                delta = calcular_delta(no_ant, c_id, no_prox)
                
                novas_rotas = [r.copy() for r in rotas]
                novas_rotas[r_idx].insert(pos, c_str)
                novas_cargas = cargas.copy()
                novas_cargas[r_idx] += dem
                
                novas_solucoes.append({
                    "rotas": novas_rotas,
                    "cargas": novas_cargas,
                    "custo": custo_base + delta,
                    "delta": delta,
                    "origem_idx": sol_idx,
                    "acao": f"Inserir na Rota {r_idx + 1} (entre {no_ant} e {no_prox})",
                    "tipo_op": "insercao"
                })
                
    # OPÇÃO B: Criar uma nova rota saindo de cada depósito até o Porto Seco
    for dep_id in dep_ids:
        custo_nova = obter_distancia(f"D_{dep_id}", c_id) + obter_distancia(c_id, f"P_{porto_id}")
        nova_rota = [f"D_{dep_id}", c_str, f"P_{porto_id}"]
        
        novas_rotas = [r.copy() for r in rotas] + [nova_rota]
        novas_cargas = cargas.copy() + [dem]
        
        novas_solucoes.append({
            "rotas": novas_rotas,
            "cargas": novas_cargas,
            "custo": custo_base + custo_nova,
            "delta": custo_nova,
            "origem_idx": sol_idx,
            "acao": f"Nova rota saindo de D_{dep_id}",
            "tipo_op": "nova_rota"
        })
        
    return novas_solucoes

def executar_beam_search(visitas, depositos, porto_id, capacidade_max, k_beam=15, verbose=False, max_opcoes_mostrar=15, max_passos_verbose=None):
    """
    Executa o Beam Search com largura de feixe K:
    - Mantém até K soluções candidatas a cada passo;
    - Ao final de cada cliente/visita, poda e retém as K melhores soluções distintas;
    - Se verbose=True, lista as opções avaliadas (inserções e novas rotas) antes da poda.
    """
    t_inicio = time.perf_counter()
    dep_ids = depositos["N_ID"].tolist()
    
    # Inicia o feixe com uma solução vazia
    beam = [{"rotas": [], "cargas": [], "custo": 0.0, "acao": "Início", "origem_idx": 0}]
    
    if verbose:
        print(f"Executando Beam Search com feixe K={k_beam}")
        print(f"Total de visitas a processar: {len(visitas)} | Capacidade do Veículo: {capacidade_max:.1f}t\n")
        
    for i, visita in enumerate(visitas, start=1):
        c_id = visita["cliente_id"]
        dem = visita["demanda"]
        tipo = visita["tipo"]
        
        candidatos = []
        
        # Expande cada solução que está no feixe atual
        for sol_idx, solucao in enumerate(beam, start=1):
            extensoes = expandir_solucao(solucao, visita, dep_ids, porto_id, capacidade_max, sol_idx=sol_idx)
            candidatos.extend(extensoes)
            
        n_ins = sum(1 for c in candidatos if c["tipo_op"] == "insercao")
        n_nov = sum(1 for c in candidatos if c["tipo_op"] == "nova_rota")
        
        # Ordena todas as extensões geradas pelo menor custo global
        candidatos.sort(key=lambda s: s["custo"])
        
        # PODA (Beam Cut): Retém as K melhores soluções distintas
        beam_novo = []
        custos_vistos = set()
        for cand in candidatos:
            c_round = round(cand["custo"], 4)
            if c_round not in custos_vistos:
                custos_vistos.add(c_round)
                beam_novo.append(cand)
                if len(beam_novo) == k_beam:
                    break
        
        # Bloco apenas para visualização detalhada do funcionamento do Beam Search
        deve_imprimir = verbose and (max_passos_verbose is None or i <= max_passos_verbose)
        
        if deve_imprimir:
            print(f"[Passo {i:02d}/{len(visitas):02d}] Cliente C_{c_id:2d} (Demanda: {dem:5.2f}t) - {tipo}")
            print("=" * 90)
            print(f"  • Feixe anterior: {len(beam)} solução(ões) ativa(s)")
            print(f"  • Total de opções geradas: {len(candidatos)} opções ({n_ins} inserções viáveis + {n_nov} novas rotas)")
            print(f"\n  --- Opções avaliadas (ordenadas do menor para o maior custo global): ---")
            
            limite = len(candidatos) if max_opcoes_mostrar is None else min(len(candidatos), max_opcoes_mostrar)
            for rank, cand in enumerate(candidatos[:limite], start=1):
                marcador = " <--- SELECIONADO NO FEIXE" if rank <= len(beam_novo) else ""
                origem_str = f"Feixe #{cand['origem_idx']}" if len(beam) > 1 else "Início"
                print(f"     [{rank:02d}] {origem_str} -> {cand['acao']:<48} | Delta: +{cand['delta']:6.2f} km | Custo: {cand['custo']:9.2f} km{marcador}")
                
            if len(candidatos) > limite:
                print(f"     ... e outras {len(candidatos) - limite} opções com custos superiores foram descartadas.")
                
            print(f"\n  ✂ Poda do Feixe (Top {len(beam_novo)} soluções retidas para o próximo passo):")
            for pos, sol in enumerate(beam_novo, start=1):
                origem_str = f"Feixe #{sol['origem_idx']} -> " if sol['origem_idx'] > 0 and len(beam) > 1 else ""
                print(f"     ✓ Feixe #{pos}: Custo = {sol['custo']:9.2f} km | {len(sol['rotas']):2d} rotas | {origem_str}{sol['acao']}")
            print(f"  ★ Menor custo global no feixe atual: {beam_novo[0]['custo']:9.2f} km\n")
            
        beam = beam_novo
        
    tempo_execucao = time.perf_counter() - t_inicio
    melhor_solucao = beam[0]
    melhor_solucao["tempo_s"] = tempo_execucao
    
    if verbose:
        print(f"✔ Construção concluída com sucesso!")
        print(f"Melhor Distância Global: {melhor_solucao['custo']:,.2f} km | Rotas: {len(melhor_solucao['rotas'])} | Tempo: {tempo_execucao:.4f} s\n")
        
    return melhor_solucao

# Visualização Passo a Passo de Todas as Opções do Beam Search
k_beam = 5                  # Largura do feixe (K)
max_opcoes_mostrar = 12     # Quantas opções listar na tela por passo (ex: 12)
max_passos_verbose = 0      # Quantos passos detalhar (ex: 10 ou 0 para execução direta)

solucao_beam_search = executar_beam_search(
    visitas, 
    depositos, 
    porto_id, 
    capacidade_veiculo, 
    k_beam=k_beam, 
    verbose=False,
    max_opcoes_mostrar=max_opcoes_mostrar,
    max_passos_verbose=max_passos_verbose)

todas_rotas = solucao_beam_search["rotas"]
distancia_final = solucao_beam_search["custo"]

# Chamada da função para calcular o resultado final
distancia_final = calcular_distancia_final(todas_rotas, df_nos)