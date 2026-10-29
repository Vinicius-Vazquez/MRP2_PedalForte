"""Módulo de persistência em SQLite sem dados de demonstração (Pronto para o cliente)."""
import os
import json
import sqlite3

PASTA_DATA = "data"
CAMINHO_DB = os.path.join(PASTA_DATA, "mrp_database.db")

def garantir_pasta_data():
    """Garante que a pasta data/ existe e inicializa a tabela no SQLite."""
    if not os.path.exists(PASTA_DATA):
        os.makedirs(PASTA_DATA)
    
    conn = sqlite3.connect(CAMINHO_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS armazenamento_json (
            nome_arquivo TEXT PRIMARY KEY,
            dados TEXT
        )
    ''')
    conn.commit()
    conn.close()

def carregar_json(nome_arquivo: str):
    """Carrega dados da base de dados SQLite simulando a leitura de arquivos JSON."""
    garantir_pasta_data()
    conn = sqlite3.connect(CAMINHO_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT dados FROM armazenamento_json WHERE nome_arquivo = ?", (nome_arquivo,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return {} if nome_arquivo in ["itens.json", "mps.json", "estrutura.json", "roteiros.json", "centros.json", "ordens.json"] else []
    
    try:
        return json.loads(row[0])
    except (json.JSONDecodeError, TypeError):
        return {} if nome_arquivo in ["itens.json", "mps.json", "estrutura.json", "roteiros.json", "centros.json", "ordens.json"] else []

def salvar_json(nome_arquivo: str, dados):
    """Salva dados na base de dados SQLite de forma permanente."""
    garantir_pasta_data()
    dados_json = json.dumps(dados, ensure_ascii=False)
    
    conn = sqlite3.connect(CAMINHO_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO armazenamento_json (nome_arquivo, dados)
        VALUES (?, ?)
    ''', (nome_arquivo, dados_json))
    conn.commit()
    conn.close()

def inicializar_base_demonstracao():
    """Função mantida para compatibilidade, mas sem injetar dados fictícios."""
    garantir_pasta_data()
    pass