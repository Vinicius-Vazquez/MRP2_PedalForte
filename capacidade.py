"""Módulo de Capacidade (CRP), Centros de Trabalho e Roteiros."""
from persistencia import carregar_json, salvar_json
from utils import ler_float, pausar

def gerenciar_capacidade():
    """Menu para gerenciar capacidade e centros de trabalho."""
    while True:
        print("\n--- CARGA X CAPACIDADE (CRP) E CENTROS DE TRABALHO ---")
        print("1. Cadastrar Centro de Trabalho")
        print("2. Cadastrar Roteiro de Operação (Item x CT x Tempo)")
        print("3. Exibir Carga x Capacidade (CRP)")
        print("0. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_centro_trabalho()
        elif opcao == "2":
            cadastrar_roteiro()
        elif opcao == "3":
            exibir_crp()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

def cadastrar_centro_trabalho():
    """Cadastra um centro de trabalho (CT)."""
    centros = carregar_json("centros.json")
    
    codigo = input("Código do Centro de Trabalho (ex: CT-01, CT-03): ").strip()
    descricao = input("Descrição do CT: ").strip()
    capacidade = ler_float("Capacidade em horas/semana: ")
    custo_hora = ler_float("Custo/hora (R$): ")
    
    centros[codigo] = {
        "codigo": codigo,
        "descricao": descricao,
        "capacidade_horas": capacidade,
        "custo_hora": custo_hora
    }
    
    salvar_json("centros.json", centros)
    print(f"Sucesso: Centro de Trabalho {codigo} salvo!")
    pausar()

def cadastrar_roteiro():
    """Vincula um item fabricado a um centro de trabalho e define o tempo unitário."""
    itens = carregar_json("itens.json")
    centros = carregar_json("centros.json")
    roteiros = carregar_json("roteiros.json")
    
    if not isinstance(roteiros, dict):
        roteiros = {}
        
    codigo_item = input("Código do Item Fabricado (PA ou SA): ").strip()
    if codigo_item not in itens or itens[codigo_item]["tipo"] == "MP":
        print("ERRO: Item não encontrado ou é matéria-prima.")
        pausar()
        return

    codigo_ct = input("Código do Centro de Trabalho: ").strip()
    if codigo_ct not in centros:
        print("ERRO: Centro de Trabalho não encontrado.")
        pausar()
        return

    tempo = ler_float("Tempo de produção por unidade (em horas): ")
    
    roteiros[codigo_item] = {
        "codigo_item": codigo_item,
        "codigo_ct": codigo_ct,
        "tempo_unitario": tempo
    }
    
    salvar_json("roteiros.json", roteiros)
    print(f"Sucesso: Roteiro para {codigo_item} cadastrado!")
    pausar()

def exibir_crp():
    """Calcula e exibe a análise de Carga x Capacidade (CRP) para um CT (RF12, RN09)."""
    centros = carregar_json("centros.json")
    ordens = carregar_json("ordens.json")
    roteiros = carregar_json("roteiros.json")
    
    if not centros:
        print("\nNenhum Centro de Trabalho cadastrado.")
        pausar()
        return

    codigo_ct = input("Digite o código do CT para análise (ex: CT-03): ").strip()
    if codigo_ct not in centros:
        print("ERRO: Centro de trabalho não encontrado.")
        pausar()
        return

    ct = centros[codigo_ct]
    cap_semanal = ct["capacidade_horas"]
    
    print(f"\nCARGA X CAPACIDADE - {codigo_ct} {ct['descricao']} ({cap_semanal:.1f} h/semana)")
    print(f"{'Sem':<4} | {'Carga(h)':<10} | {'Uso(%)':<8} | Gráfico")
    print("-" * 55)

    # Inicializar carga acumulada para cada semana (1 a 8)
    carga_semanal = {i: 0.0 for i in range(1, 9)}
    
    if isinstance(ordens, list):
        for o in ordens:
            # Considera OPs que consomem capacidade no CT
            item_cod = o["codigo_item"]
            status = o.get("status", "")
            if item_cod in roteiros and roteiros[item_cod]["codigo_ct"] == codigo_ct:
                # RN09: Considera ordens que exigem trabalho na semana de liberação/entrega
                sem = o.get("semana_liberacao", 1)
                if 1 <= sem <= 8:
                    tempo_un = roteiros[item_cod]["tempo_unitario"]
                    carga_semanal[sem] += o["quantidade"] * tempo_un

    sobrecarga_detectada = False
    for sem in range(1, 9):
        carga = carga_semanal[sem]
        uso = (carga / cap_semanal * 100) if cap_semanal > 0 else 0
        barras = "#" * int(uso // 10)
        
        status_txt = ""
        if uso > 100:
            status_txt = " SOBRECARGA"
            sobrecarga_detectada = True

        print(f"{sem:<4} | {carga:<10.1f} | {uso:<8.0f} {barras:<12} {status_txt}")

    if sobrecarga_detectada:
        print("\nSugestão: Antecipar OPs ou programar hora extra nas semanas com sobrecarga.")
    pausar()