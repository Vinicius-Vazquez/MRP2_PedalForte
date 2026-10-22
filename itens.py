"""Módulo de cadastro de itens (PA, SA, MP)."""
from persistencia import carregar_json, salvar_json
from utils import ler_inteiro, ler_float, pausar

def gerenciar_itens():
    """Menu para gerenciar o cadastro de itens."""
    while True:
        print("\n--- GESTÃO DE ITENS ---")
        print("1. Cadastrar Item")
        print("2. Listar Itens")
        print("3. Alterar Item")
        print("0. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_item()
        elif opcao == "2":
            listar_itens()
        elif opcao == "3":
            alterar_item()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

def cadastrer_dados_item(codigo: str):
    """Auxiliar para coletar dados de um item."""
    descricao = input("Descrição do item: ")
    while True:
        tipo = input("Tipo (PA - Produto Acabado, SA - Semiacabado, MP - Matéria-prima): ").upper()
        if tipo in ["PA", "SA", "MP"]:
            break
        print("Tipo inválido. Escolha PA, SA ou MP.")
        
    unidade = input("Unidade de medida (ex: un, m, L): ")
    custo_unitario = ler_float("Custo unitário (R$): ")
    lead_time = ler_inteiro("Lead time (semanas): ")
    estoque_seguranca = ler_inteiro("Estoque de segurança: ")
    lote_minimo = ler_inteiro("Lote mínimo: ")
    
    return {
        "codigo": codigo,
        "descricao": descricao,
        "tipo": tipo,
        "unidade": unidade,
        "custo_unitario": custo_unitario,
        "lead_time": lead_time,
        "estoque_seguranca": estoque_seguranca,
        "lote_minimo": lote_minimo
    }

def cadastrar_item():
    """Cadastra um novo item no sistema."""
    print("\n--- CADASTRAR NOVO ITEM ---")
    codigo = input("Código do item (ex: PA-003, SA-030, MP-400): ").strip()
    
    itens = carregar_json("itens.json")
    if codigo in itens:
        print(f"ERRO: O item {codigo} já está cadastrado.")
        pausar()
        return
        
    novo_item = cadastrer_dados_item(codigo)
    itens[codigo] = novo_item
    salvar_json("itens.json", itens)
    print(f"Sucesso: Item {codigo} cadastrado com sucesso!")
    pausar()

def listar_itens():
    """Lista todos os itens cadastrados."""
    itens = carregar_json("itens.json")
    if not itens:
        print("\nNenhum item cadastrado.")
        pausar()
        return
        
    print("\n--- LISTA DE ITENS ---")
    print(f"{'Código':<10} | {'Tipo'}<6 | {'Un'}<4 | {'Est.Seg'}<8 | {'Lote Min'}<8 | {'Descrição'}")
    print("-" * 65)
    for codigo, item in sorted(itens.items()):
        print(f"{codigo:<10} | {item['tipo']:<6} | {item['unidade']:<4} | {item['estoque_seguranca']:<8} | {item['lote_minimo']:<8} | {item['descricao']}")
    pausar()

def alterar_item():
    """Altera dados de um item existente."""
    itens = carregar_json("itens.json")
    codigo = input("Digite o código do item que deseja alterar: ").strip()
    
    if codigo not in itens:
        print(f"ERRO: Item {codigo} não encontrado.")
        pausar()
        return
        
    print(f"Alterando dados do item {codigo} ({itens[codigo]['descricao']}):")
    dados_atualizados = cadastrer_dados_item(codigo)
    itens[codigo] = dados_atualizados
    salvar_json("itens.json", itens)
    print(f"Sucesso: Item {codigo} atualizado!")
    pausar()