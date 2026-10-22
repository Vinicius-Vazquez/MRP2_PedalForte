"""Módulo de exportação de relatórios em CSV (RF14)."""
import os
import csv
from persistencia import carregar_json
from estoque import calcular_saldo_atual
from utils import pausar

def exportar_relatorios_csv():
    """Exporta a posição de estoque e a lista de ordens para CSV (RF14)."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    itens = carregar_json("itens.json")
    ordens = carregar_json("ordens.json")
    
    caminho_estoque = "data/posicao_estoque.csv"
    with open(caminho_estoque, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["codigo", "descricao", "tipo", "unidade", "estoque_atual", "estoque_seguranca"])
        for codigo, item in itens.items():
            saldo = calcular_saldo_atual(codigo)
            writer.writerow([codigo, item["descricao"], item["tipo"], item["unidade"], saldo, item["estoque_seguranca"]])
            
    caminho_ordens = "data/ordens_export.csv"
    with open(caminho_ordens, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "tipo", "codigo_item", "quantidade", "semana_liberacao", "semana_entrega", "status"])
        if isinstance(ordens, list):
            for o in ordens:
                writer.writerow([o.get("id"), o.get("tipo"), o.get("codigo_item"), o.get("quantidade"), o.get("semana_liberacao"), o.get("semana_entrega"), o.get("status")])
                
    print("\nSucesso: Relatórios exportados para a pasta data/ (posicao_estoque.csv e ordens_export.csv)!")
    pausar()