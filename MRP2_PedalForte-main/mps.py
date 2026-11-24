"""Módulo de gerenciamento do Plano Mestre de Produção (MPS) para horizonte de 8 semanas (RF07)."""

HORIZONTE_SEMANAS = 8

def gerenciar_mps(dados: dict) -> None:
    """Permite visualizar, cadastrar e alterar a demanda semanal dos produtos acabados (PA) (RF07)."""
    print("\n--- PLANO MESTRE DE PRODUÇÃO (MPS) ---")
    
    # Filtra apenas os Produtos Acabados (PA) cadastrados
    produtos_acabados = [cod for cod, item in dados["itens"].items() if item["tipo"] == "PA"]
    
    if not produtos_acabados:
        print("ERRO: Nenhum Produto Acabado (PA) cadastrado no sistema.")
        return

    print("Produtos Acabados disponíveis:")
    for idx, pa in enumerate(produtos_acabados, 1):
        desc = dados["itens"][pa]["descricao"]
        print(f"{idx}. {pa} - {desc}")

    try:
        escolha = int(input("Escolha o número do produto para gerenciar o MPS: ").strip())
        if escolha < 1 or escolha > len(produtos_acabados):
            print("ERRO: Opção inválida.")
            return
    except ValueError:
        print("ERRO: Valor numérico inválido.")
        return

    pa_selecionado = produtos_acabados[escolha - 1]
    
    # Garante que o PA possui uma lista de 8 semanas inicializada no mps
    if pa_selecionado not in dados["mps"] or len(dados["mps"][pa_selecionado]) != HORIZONTE_SEMANAS:
        dados["mps"][pa_selecionado] = [0.0] * HORIZONTE_SEMANAS

    demandas = dados["mps"][pa_selecionado]

    while True:
        print(f"\n--- MPS ATUAL - {pa_selecionado} ({dados['itens'][pa_selecionado]['descricao']}) ---")
        print(f"{'Semana':<10} | " + " | ".join([f"Sem {i}" for i in range(1, HORIZONTE_SEMANAS + 1)]))
        print("-" * 75)
        print(f"Demanda   | " + " | ".join([f"{int(d):<5}" for d in demandas]))
        print("-" * 75)
        print("1. Alterar demanda de uma semana específica")
        print("0. Salvar e voltar ao menu principal")
        
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            try:
                semana = int(input(f"Digite o número da semana (1 a {HORIZONTE_SEMANAS}): ").strip())
                if semana < 1 or semana > HORIZONTE_SEMANAS:
                    print(f"ERRO: A semana deve estar entre 1 e {HORIZONTE_SEMANAS}.")
                    continue
                nova_demanda = float(input(f"Nova demanda para a semana {semana}: ").strip())
                if nova_demanda < 0:
                    print("ERRO: A demanda não pode ser negativa.")
                    continue
                demandas[semana - 1] = nova_demanda
                dados["mps"][pa_selecionado] = demandas
                print(f"Sucesso: Demanda da semana {semana} atualizada para {nova_demanda:.1f}!")
            except ValueError:
                print("ERRO: Valores numéricos inválidos.")
        elif op == "0":
            print("Plano Mestre de Produção salvo com sucesso!")
            break
        else:
            print("ERRO: Opção inválida.")