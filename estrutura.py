"""Módulo de gerenciamento e explosão da Estrutura de Produto (BOM) em até 3 níveis (RF03, RN03)."""


def _iterar_componentes(estrutura_pai) -> list[tuple[str, float]]:
    """Normaliza os componentes de um item pai como pares (codigo_filho, quantidade)."""
    if isinstance(estrutura_pai, dict):
        return [(str(filho), float(qtd)) for filho, qtd in estrutura_pai.items()]
    if isinstance(estrutura_pai, list):
        pares: list[tuple[str, float]] = []
        for comp in estrutura_pai:
            if isinstance(comp, dict) and "componente" in comp and "quantidade" in comp:
                pares.append((str(comp["componente"]), float(comp["quantidade"])))
        return pares
    return []


def cadastrar_estrutura(dados: dict) -> None:
    """Cadastra os componentes (filhos) de um item pai, respeitando os níveis (PA -> SA -> MP) (RF03, RN03)."""
    print("\n--- CADASTRO DE ESTRUTURA (BOM) ---")
    pai = input("Código do item Pai (ex: PA-001, SA-010): ").strip().upper()

    if pai not in dados["itens"]:
        print(f"ERRO: O item pai {pai} não está cadastrado no sistema.")
        return

    tipo_pai = dados["itens"][pai]["tipo"]
    if tipo_pai == "MP":
        print("ERRO: Matérias-primas (MP) são compradas e não possuem estrutura de componentes (RN03).")
        return

    print(f"Item Pai selecionado: {pai} ({dados['itens'][pai]['descricao']}) [Tipo: {tipo_pai}]")

    filho = input("Código do componente filho (ex: SA-010, MP-100): ").strip().upper()
    if filho not in dados["itens"]:
        print(f"ERRO: O componente {filho} não está cadastrado no sistema.")
        return

    if pai == filho:
        print("ERRO: Um item não pode ser componente dele mesmo (ciclo na BOM).")
        return

    tipo_filho = dados["itens"][filho]["tipo"]

    # Validação de regras de nível (RN03: PA pode ter SA e MP; SA apenas MP)
    if tipo_pai == "PA" and tipo_filho not in ["SA", "MP"]:
        print("ERRO: Um Produto Acabado (PA) só pode ter Semiacabados (SA) ou Matérias-Primas (MP) como filhos.")
        return
    if tipo_pai == "SA" and tipo_filho != "MP":
        print("ERRO (RN03): Um Semiacabado (SA) só pode ter Matérias-Primas (MP) como componentes diretos.")
        return

    try:
        quantidade = float(
            input(f"Quantidade unitária de {filho} necessária para 1 unidade de {pai}: ").strip()
        )
        if quantidade <= 0:
            print("ERRO: A quantidade deve ser maior que zero.")
            return
    except ValueError:
        print("ERRO: Valor numérico inválido.")
        return

    if pai not in dados["estrutura"] or not isinstance(dados["estrutura"][pai], dict):
        dados["estrutura"][pai] = {}

    ja_existia = filho in dados["estrutura"][pai]
    dados["estrutura"][pai][filho] = quantidade

    if ja_existia:
        print(f"Sucesso: Quantidade do componente {filho} atualizada no pai {pai}!")
    else:
        print(f"Sucesso: Componente {filho} ({quantidade} un) adicionado à estrutura de {pai}!")


def exibir_bom_indenta(codigo: str, dados: dict, nivel: int = 0) -> None:
    """Exibe recursivamente a árvore de produto de forma indentada (explosão da BOM) (RF03)."""
    if nivel == 0:
        if codigo not in dados["itens"]:
            print(f"ERRO: Item {codigo} não encontrado.")
            return
        item = dados["itens"][codigo]
        print(f"\n>> Código do produto: {codigo}")
        print(f"\n{codigo} {item['descricao']} ({item['unidade']})")

    if codigo in dados["estrutura"]:
        for filho_cod, qtd in _iterar_componentes(dados["estrutura"][codigo]):
            if filho_cod in dados["itens"]:
                filho_item = dados["itens"][filho_cod]
                tracos = "|   " * nivel + "|--- "
                print(f"{tracos}{filho_cod} {filho_item['descricao']} ........ {qtd} {filho_item['unidade']}")
                exibir_bom_indenta(filho_cod, dados, nivel + 1)


def gerenciar_estrutura(dados: dict) -> None:
    """Submenu para gerenciamento e visualização da Estrutura de Produto."""
    while True:
        print("\n--- GESTÃO DE ESTRUTURA DE PRODUTO (BOM) ---")
        print("1. Cadastrar componente na estrutura")
        print("2. Exibir árvore de produto indentada (Explosão BOM)")
        print("0. Voltar ao menu anterior")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            cadastrar_estrutura(dados)
        elif op == "2":
            cod = input("Digite o código do Produto Acabado (ex: PA-001): ").strip().upper()
            exibir_bom_indenta(cod, dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
            