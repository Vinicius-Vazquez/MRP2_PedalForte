"""Módulo de gráficos de gestão com matplotlib (RF16)."""
import os
import matplotlib.pyplot as plt
from persistencia import carregar_json
from estoque import calcular_saldo_atual
from utils import pausar

def gerar_graficos():
    """Gera gráficos de gestão e acompanhamento salvando em PNG e exibindo na tela (RF16)."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    itens = carregar_json("itens.json")
    if not itens:
        print("Nenhum item cadastrado para gerar gráficos.")
        pausar()
        return

    codigos = list(itens.keys())[:10]
    saldos = [calcular_saldo_atual(c) for c in codigos]
    seguranca = [itens[c]["estoque_seguranca"] for c in codigos]

    plt.figure(figsize=(10, 5))
    x = range(len(codigos))
    plt.bar(x, saldos, width=0.4, label="Saldo Atual", color="blue", align="center")
    plt.bar([p + 0.4 for p in x], seguranca, width=0.4, label="Estoque de Segurança", color="orange", align="center")
    plt.xticks([p + 0.2 for p in x], codigos, rotation=45)
    plt.ylabel("Quantidade")
    plt.title("Posição de Estoque: Saldo Atual vs Estoque de Segurança")
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/grafico_estoque.png")
    plt.show()
    plt.close()

    print("Sucesso: Gráfico de estoque gerado e salvo em data/grafico_estoque.png!")
    pausar()