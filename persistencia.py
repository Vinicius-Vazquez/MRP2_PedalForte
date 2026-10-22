"""Módulo de persistência: manipulação de arquivos JSON e CSV."""
import os
import json
import csv

PASTA_DATA = "data"

def garantir_pasta_data():
    """Garante que a pasta data/ existe."""
    if not os.path.exists(PASTA_DATA):
        os.makedirs(PASTA_DATA)

def carregar_json(nome_arquivo: str):
    """Carrega dados de um arquivo JSON dentro da pasta data/."""
    garantir_pasta_data()
    caminho = os.path.join(PASTA_DATA, nome_arquivo)
    if not os.path.exists(caminho):
        return {} if nome_arquivo in ["itens.json", "mps.json"] else []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar_json(nome_arquivo: str, dados):
    """Salva dados em um arquivo JSON dentro da pasta data/."""
    garantir_pasta_data()
    caminho = os.path.join(PASTA_DATA, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def inicializar_base_demonstracao():
    """Inicializa a base de demonstração padrão (RNF09) se os arquivos estiverem vazios."""
    itens = carregar_json("itens.json")
    if not itens:
        itens_demo = {
            "PA-001": {"codigo": "PA-001", "descricao": "Bicicleta Aro 29 MTB", "tipo": "PA", "unidade": "un", "custo_unitario": 0.0, "lead_time": 1, "estoque_seguranca": 5, "lote_minimo": 10},
            "PA-002": {"codigo": "PA-002", "descricao": "Bicicleta Aro 29 Speed", "tipo": "PA", "unidade": "un", "custo_unitario": 0.0, "lead_time": 1, "estoque_seguranca": 3, "lote_minimo": 10},
            "SA-010": {"codigo": "SA-010", "descricao": "Quadro aro 29 soldado", "tipo": "SA", "unidade": "un", "custo_unitario": 0.0, "lead_time": 1, "estoque_seguranca": 10, "lote_minimo": 20},
            "SA-020": {"codigo": "SA-020", "descricao": "Roda aro 29 montada", "tipo": "SA", "unidade": "un", "custo_unitario": 0.0, "lead_time": 1, "estoque_seguranca": 10, "lote_minimo": 80},
            "MP-100": {"codigo": "MP-100", "descricao": "Tubo de aco carbono", "tipo": "MP", "unidade": "m", "custo_unitario": 25.0, "lead_time": 1, "estoque_seguranca": 50, "lote_minimo": 100},
            "MP-101": {"codigo": "MP-101", "descricao": "Tinta epoxi", "tipo": "MP", "unidade": "L", "custo_unitario": 40.0, "lead_time": 1, "estoque_seguranca": 20, "lote_minimo": 50},
            "MP-200": {"codigo": "MP-200", "descricao": "Aro 29 aluminio", "tipo": "MP", "unidade": "un", "custo_unitario": 45.0, "lead_time": 1, "estoque_seguranca": 40, "lote_minimo": 100},
            "MP-201": {"codigo": "MP-201", "descricao": "Raio inox", "tipo": "MP", "unidade": "un", "custo_unitario": 1.5, "lead_time": 1, "estoque_seguranca": 200, "lote_minimo": 500},
            "MP-202": {"codigo": "MP-202", "descricao": "Pneu 29 x 2.20", "tipo": "MP", "unidade": "un", "custo_unitario": 35.0, "lead_time": 1, "estoque_seguranca": 20, "lote_minimo": 60},
            "MP-300": {"codigo": "MP-300", "descricao": "Guidao", "tipo": "MP", "unidade": "un", "custo_unitario": 45.0, "lead_time": 1, "estoque_seguranca": 15, "lote_minimo": 30},
            "MP-301": {"codigo": "MP-301", "descricao": "Kit transmissao 12v", "tipo": "MP", "unidade": "un", "custo_unitario": 320.0, "lead_time": 2, "estoque_seguranca": 10, "lote_minimo": 20},
            "MP-302": {"codigo": "MP-302", "descricao": "Selim ergonomico", "tipo": "MP", "unidade": "un", "custo_unitario": 60.0, "lead_time": 1, "estoque_seguranca": 15, "lote_minimo": 30}
        }
        salvar_json("itens.json", itens_demo)

    centros = carregar_json("centros.json")
    if not centros:
        centros_demo = {
            "CT-01": {"codigo": "CT-01", "descricao": "Soldagem de Quadros", "capacidade_horas": 40.0, "custo_hora": 50.0},
            "CT-03": {"codigo": "CT-03", "descricao": "Montagem final", "capacidade_horas": 16.0, "custo_hora": 65.0}
        }
        salvar_json("centros.json", centros_demo)