"""Módulo de cálculo de custo padrão dos produtos (materiais + centros de trabalho) (RF13)."""

from utils import iterar_componentes


def calcular_custo_produto(codigo: str, dados: dict, visitados=None) -> float:
    """Calcula recursivamente o custo padrão de um item (PA, SA ou MP) (RF13)."""
    if visitados is None:
        visitados = set()

    if codigo in visitados:
        return 0.0  # Proteção contra ciclos

    visitados.add(codigo)

    if codigo not in dados.get("itens", {}):
        return 0.0

    item = dados["itens"][codigo]
    tipo = item["tipo"]

    # Se for Matéria-Prima, o custo é o custo unitário direto cadastrado
    if tipo == "MP":
        return float(item.get("custo_unitario", 0.0))

    # Se for PA ou SA, o custo é a soma do custo dos componentes filhos + custo de processamento no centro
    custo_total = 0.0

    # 1. Custo dos materiais componentes (BOM)
    estrutura = dados.get("estrutura", {})
    if codigo in estrutura:
        for filho_cod, qtd in iterar_componentes(estrutura[codigo]):
            custo_filho = calcular_custo_produto(filho_cod, dados, visitados.copy())
            custo_total += custo_filho * qtd

    # 2. Custo de processamento baseado no roteiro e centro de trabalho
    roteiros = dados.get("roteiros", {})
    centros = dados.get("centros", {})
    if codigo in roteiros:
        roteiro = roteiros[codigo]
        ct_cod = roteiro.get("centro")
        tempo_unitario = float(roteiro.get("tempo_unitario", 0.0))  # em horas

        if ct_cod in centros:
            custo_hora = float(centros[ct_cod].get("custo_hora", 0.0))
            custo_total += tempo_unitario * custo_hora

    return custo_total


def gerenciar_custos(dados: dict) -> None:
    """Calcula e exibe o relatório de custo padrão de todos os produtos do sistema (RF13)."""
    print("\n--- RELATÓRIO DE CUSTO PADRÃO DOS PRODUTOS ---")

    if not dados.get("itens"):
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
