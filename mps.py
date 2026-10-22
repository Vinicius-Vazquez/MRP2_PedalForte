"""Módulo do Plano Mestre de Produção (MPS)."""
from persistencia import carregar_json, salvar_json
from utils import ler_inteiro, pausar

def gerenciar_mps():
    """Menu para gerenciar o Plano Mestre de Produção."""
    while True:
        print("\n--- PLANO MESTRE DE PRODUÇÃO (MPS) ---")
        print("1. Cadastrar / Alterar Demandas Semanais (8 Semanas)")
        print("2. Visualizar MPS")
        print("0. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_ou_alterar_mps()
        elif opcao == "2":
            visualizar_mps()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

def cadastrar_ou_alterar_mps():
    """Define as demandas de produtos acabados (PA) para um horizonte de 8 semanas."""
    itens = carregar_json("itens.json")
    mps = carregar_json("mps.json")
    
    codigo = input("Digite o código do Produto Acabado (PA): ").strip()
    if codigo not in itens or itens[codigo]["tipo"] != "PA":
        print("ERRO: Item não encontrado ou não é um Produto Acabado (PA).")
        pausar()
        return

    print(f"\nDefinindo MPS para {codigo} - {itens[codigo]['descricao']}")
    semanas = {}
    for sem in range(1, 9):
        demand = ler_inteiro(f"Demanda para Semana {sem}: ")
        semanas[f"S{sem}"] = demand
        
    mps[codigo] = semanas
    salvar_json("mps.json", mps)
    print(f"Sucesso: MPS atualizado para {codigo}!")
    pausar()

def visualizar_mps():
    """Exibe o Plano Mestre de Produção cadastrado."""
    itens = carregar_json("itens.json")
    mps = carregar_json("mps.json")
    
    if not mps:
        print("\nNenhum MPS cadastrado.")
        pausar()
        return

    print("\n--- PLANO MESTRE DE PRODUÇÃO (MPS) ---")
    header = f"{'Código PA':<10} | {'Descrição':<25}" + "".join([f" | S{i:<2}" for i in range(1, 9)])
    print(header)
    print("-" * len(header))

    for codigo, semanas in mps.items():
        desc = itens.get(codigo, {}).get('descricao', 'N/A')[:25]
        linha = f"{codigo:<10} | {desc:<25}"
        for i in range(1, 9):
            linha += f" | {semanas.get(f'S{i}', 0):<3}"
        print(linha)

    pausar()