"""Módulo de emissão de relatórios gerenciais e exportação de dados em CSV (RF15, RNF07)."""

import csv
import os

DIRETORIO_DADOS = "data"


def exportar_relatorio_estoque(dados: dict) -> None:
    """Exporta o saldo atual e os movimentos de estoque para um arquivo CSV dedicado (RF15)."""
    print("\n--- EXPORTANDO RELATÓRIO DE ESTOQUE (CSV) ---")
    
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    caminho_csv = os.path.join(DIRETORIO_DADOS, "relatorio_estoque_atual.csv")
    
    try:
        with open(caminho_csv, "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Codigo", "Descricao", "Tipo", "Unidade", "Saldo Atual", "Estoque Seguranca", "Custo Unitario (R$)"])
            
            for codigo, item in sorted(dados["itens"].items()):
                saldo = dados["estoque"].get(codigo, {}).get("saldo_atual", 0.0)
                escritor.writerow([
                    codigo,
                    item["descricao"],
                    item["tipo"],
                    item["unidade"],
                    saldo,
                    item["estoque_seguranca"],
                    f"{item['custo_unitario']:.2f}"
                ])
                
        print(f"Sucesso: Relatório de estoque exportado para '{caminho_csv}'!")
    except Exception as e:
        print(f"ERRO: Não foi possível exportar o arquivo: {e}")


def exportar_relatorio_ordens(dados: dict) -> None:
    """Exporta todas as ordens de produção e compra para um arquivo CSV (RF15)."""
    print("\n--- EXPORTANDO RELATÓRIO DE ORDENS (CSV) ---")
    
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    caminho_csv = os.path.join(DIRETORIO_DADOS, "relatorio_ordens.csv")
    ordens = dados.get("ordens", {})
    
    try:
        with open(caminho_csv, "w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Ordem", "Tipo", "Item", "Quantidade", "Semana", "Status"])
            
            for num_ordem, ord_info in sorted(ordens.items()):
                escritor.writerow([
                    num_ordem,
                    ord_info["tipo"],
                    ord_info["item"],
                    ord_info["quantidade"],
                    ord_info["semana"],
                    ord_info["status"]
                ])
                
        print(f"Sucesso: Relatório de ordens exportado para '{caminho_csv}'!")
    except Exception as e:
        print(f"ERRO: Não foi possível exportar o arquivo: {e}")


def gerenciar_relatorios(dados: dict) -> None:
    """Submenu para emissão e exportação de relatórios."""
    while True:
        print("\n--- GESTÃO DE RELATÓRIOS E EXPORTAÇÃO (CSV) ---")
        print("1. Exportar relatório de estoque atual para CSV")
        print("2. Exportar relatório de ordens (OP/OC) para CSV")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            exportar_relatorio_estoque(dados)
        elif op == "2":
            exportar_relatorio_ordens(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
