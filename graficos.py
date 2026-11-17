"""Módulo de visualização gráfica de dados e indicadores usando Matplotlib."""

import matplotlib.pyplot as plt

def gerar_grafico_estoque(dados: dict) -> None:
    """Gera um gráfico de barras comparando o saldo atual com o estoque de segurança dos itens."""
    print("\n--- GERANDO GRÁFICO DE ESTOQUE ---")
    
    if not dados["itens"]:
        print("ERRO: Nenhum item cadastrado.")
        return

    codigos = []
    saldos = []
    seguranca = []

    for codigo, item in sorted(dados["itens"].items()):
        codigos.append(codigo)
        saldos.append(dados["estoque"].get(codigo, {}).get("saldo_atual", 0.0))
        seguranca.append(item["estoque_seguranca"])

    plt.figure(figsize=(10, 6))
    x = range(len(codigos))
    largura = 0.35

    plt.bar([i - largura/2 for i in x], saldos, largura, label="Saldo Atual", color="steelblue")
    plt.bar([i + largura/2 for i in x], seguranca, largura, label="Estoque de Segurança", color="indianred")

    plt.xlabel("Códigos dos Itens")
    plt.ylabel("Quantidade")
    plt.title("Comparativo: Saldo Atual x Estoque de Segurança")
    plt.xticks(x, codigos, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    
    print("Exibindo janela do gráfico... (Feche a janela do gráfico para retornar ao sistema)")
    plt.show()

def gerenciar_graficos(dados: dict) -> None:
    """Submenu para visualização de gráficos gerenciais."""
    while True:
        print("\n--- GRÁFICOS DE GESTÃO ---")
        print("1. Gráfico comparativo de Estoque x Estoque de Segurança")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            gerenar_grafico_estoque(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")