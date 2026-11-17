"""Módulo de persistência para leitura e salvamento de dados em arquivos JSON e CSV (RF15, RNF07)."""

import json
import os

DIRETORIO_DADOS = "data"

def carregar_dados() -> dict:
    """Carrega todos os dados dos arquivos JSON na pasta data/ ao iniciar o sistema."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    dados = {
        "itens": {},
        "estrutura": {},
        "estoque": {},
        "centros": {},
        "roteiros": {},
        "mps": {},
        "ordens": {},
        "movimentos": []
    }

    arquivos = {
        "itens": "itens.json",
        "estrutura": "estrutura.json",
        "estoque": "estoque.json",
        "centros": "centros.json",
        "roteiros": "roteiros.json",
        "mps": "mps.json",
        "ordens": "ordens.json"
    }

    for chave, nome_arquivo in arquivos.items():
        caminho = os.path.join(DIRETORIO_DADOS, nome_arquivo)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados[chave] = json.load(f)
            except Exception as e:
                print(f"Aviso: Não foi possível carregar {nome_arquivo}: {e}")

    return dados

def salvar_dados(dados: dict) -> None:
    """Salva todos os dicionários do sistema nos arquivos JSON da pasta data/."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    arquivos = {
        "itens": "itens.json",
        "estrutura": "estrutura.json",
        "estoque": "estoque.json",
        "centros": "centros.json",
        "roteiros": "roteiros.json",
        "mps": "mps.json",
        "ordens": "ordens.json"
    }

    for chave, nome_arquivo in arquivos.items():
        caminho = os.path.join(DIRETORIO_DADOS, nome_arquivo)
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados[chave], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERRO: Não foi possível salvar {nome_arquivo}: {e}")