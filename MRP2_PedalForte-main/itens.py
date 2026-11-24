"""Módulo de cadastro, listagem e alteração de itens do Sistema MRP II (RF02, RN01)."""

TIPOS_VALIDOS = {"PA": "Produto Acabado", "SA": "Semiacabado", "MP": "Matéria-Prima"}

def validar_codigo_item(codigo: str) -> bool:
    """Valida se o código do item segue estritamente o formato Tipo-Número (ex: PA-001, SA-020)."""
    partes = codigo.strip().upper().split("-")
    if len(partes) != 2:
        return False
    tipo, num = partes[0], partes[1]
    return tipo in TIPOS_VALIDOS and num.isdigit()

def cadastrar_item(dados: dict) -> None:
    """Cadastra um novo item aplicando as regras de negócio de formato e unicidade (RF02, RN01)."""
    print("\n--- CADASTRO DE NOVO ITEM ---")
    codigo = input("Digite o código do item (ex: PA-001, SA-010, MP-100): ").strip().upper()
    
    if not validar_codigo_item(codigo):
        print("ERRO: Código inválido! O formato deve ser Tipo-Número (ex: PA-001, SA-010, MP-100).")
        return
    
    if codigo in dados["itens"]:
        print(f"ERRO: Já existe um item cadastrado com o código {codigo}.")
        return

    tipo_sigla = codigo.split("-")[0]
    print(f"Tipo identificado: {TIPOS_VALIDOS[tipo_sigla]}")

    descricao = input("Descrição do item: ").strip()
    if not descricao:
        print("ERRO: A descrição não pode ser vazia.")
        return

    try:
        unidade = input("Unidade de medida (ex: un, m, L, kg): ").strip()
        custo_unitario = float(input("Custo unitário (R$): ").strip())
        lead_time = int(input("Lead time (em semanas): ").strip())
        estoque_seguranca = float(input("Estoque de segurança: ").strip())
        lote_minimo = float(input("Lote mínimo de compra/produção: ").strip())
    except ValueError:
        print("ERRO: Valores numéricos inválidos inseridos. Operação cancelada.")
        return

    # Registra o item no dicionário principal
    dados["itens"][codigo] = {
        "codigo": codigo,
        "tipo": tipo_sigla,
        "descricao": descricao,
        "unidade": unidade,
        "custo_unitario": custo_unitario,
        "lead_time": lead_time,
        "estoque_seguranca": estoque_seguranca,
        "lote_minimo": lote_minimo
    }

    # Garante estrutura de estoque inicial caso não exista
    if codigo not in dados["estoque"]:
        dados["estoque"][codigo] = {"saldo_atual": 0.0}

    print(f"Sucesso: Item {codigo} cadastrado com sucesso!")

def listar_itens(dados: dict) -> None:
    """Lista todos os itens cadastrados no sistema de forma organizada (RF02)."""
    print("\n--- LISTA DE ITENS CADASTRADOS ---")
    if not dados["itens"]:
        print("Nenhum item cadastrado até o momento.")
        return

    print(f"{'Código':<10} | {'Tipo':<5} | {'Descrição':<30} | {'Un':<4} | {'Custo (R$)':<10} | {'LT':<3} | {'Est.Seg':<8} | {'Lote Mín':<8}")
    print("-" * 95)
    for codigo, item in sorted(dados["itens"].items()):
        print(f"{codigo:<10} | {item['tipo']:<5} | {item['descricao']:<30} | {item['unidade']:<4} | {item['custo_unitario']:<10.2f} | {item['lead_time']:<3} | {item['estoque_seguranca']:<8.1f} | {item['lote_minimo']:<8.1f}")

def gerenciar_itens(dados: dict) -> None:
    """Submenu para gerenciamento de itens."""
    while True:
        print("\n--- GESTÃO DE ITENS ---")
        print("1. Cadastrar novo item")
        print("2. Listar itens cadastrados")
        print("0. Voltar ao menu anterior")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            cadastrar_item(dados)
        elif op == "2":
            listar_itens(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")