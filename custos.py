"""Módulo de cálculo de custo padrão dos produtos (materiais + centros de trabalho) (RF13)."""


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


def calcular_custo_produto(codigo: str, dados: dict, visitados=None) -> float:
    """Calcula recursivamente o custo padrão de um item (PA, SA ou MP) (RF13)."""
    if visitados is None:
        visitados = set()

    if codigo in visitados:
        return 0.0  # Proteção contra ciclos

    visitados.add(codigo)

    if codigo not in dados["itens"]:
        return 0.0

    item = dados["itens"][codigo]
    tipo = item["tipo"]

    # Se for Matéria-Prima, o custo é o custo unitário direto cadastrado
    if tipo == "MP":
        return float(item["custo_unitario"])

    # Se for PA ou SA, o custo é a soma do custo dos componentes filhos + custo de processamento no centro
    custo_total = 0.0

    # 1. Custo dos materiais componentes (BOM)
    if codigo in dados["estrutura"]:
        for filho_cod, qtd in _iterar_componentes(dados["estrutura"][codigo]):
            custo_filho = calcular_custo_produto(filho_cod, dados, visitados.copy())
            custo_total += custo_filho * qtd

    # 2. Custo de processamento baseado no roteiro e centro de trabalho
    if codigo in dados["roteiros"]:
        roteiro = dados["roteiros"][codigo]
        ct_cod = roteiro["centro"]
        tempo_unitario = float(roteiro["tempo_unitario"])  # em horas

        if ct_cod in dados["centros"]:
            custo_hora = float(dados["centros"][ct_cod]["custo_hora"])
            custo_total += tempo_unitario * custo_hora

    return custo_total


def gerenciar_custos(dados: dict) -> None:
    """Calcula e exibe o relatório de custo padrão de todos os produtos do sistema (RF13)."""
    print("\n--- RELATÓRIO DE CUSTO PADRÃO DOS PRODUTOS ---")

    if not dados["itens"]:
        print("ERRO: Nenhum item cadastrado.")
        return

    print(f"{'Código':<10} | {'Tipo':<5} | {'Descrição':<35} | {'Custo Padrão (R$)':<15}")
    print("-" * 75)

    for codigo, item in sorted(dados["itens"].items()):
        custo = calcular_custo_produto(codigo, dados)
        # Atualiza o custo unitário calculado no dicionário do item
        item["custo_unitario"] = custo
        print(f"{codigo:<10} | {item['tipo']:<5} | {item['descricao']:<35} | R$ {custo:<12.2f}")

    print("-" * 75)
    print("Cálculo e atualização de custos padrões concluídos com sucesso!")
    