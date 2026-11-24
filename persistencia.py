"""Módulo de persistência para leitura e salvamento de dados em arquivos JSON e CSV (RF15, RNF07)."""

import csv
import json
import os

DIRETORIO_DADOS = "data"
ARQUIVO_MOVIMENTOS = "movimentos.csv"
COLUNAS_MOVIMENTOS = ["data", "item", "tipo", "quantidade", "saldo", "documento"]


def _carregar_movimentos_csv(caminho_csv: str) -> list[dict]:
    """Lê o histórico de movimentações (Kardex) de data/movimentos.csv."""
    if not os.path.exists(caminho_csv):
        return []

    movimentos: list[dict] = []
    try:
        with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            for linha in leitor:
                if not linha or not linha.get("item"):
                    continue
                try:
                    quantidade = float(str(linha.get("quantidade", "0")).replace(",", "."))
                    saldo = float(str(linha.get("saldo", "0")).replace(",", "."))
                except ValueError:
                    continue

                movimentos.append({
                    "data": str(linha.get("data", "")).strip(),
                    "item": str(linha.get("item", "")).strip().upper(),
                    "tipo": str(linha.get("tipo", "")).strip().upper(),
                    "quantidade": quantidade,
                    "saldo": saldo,
                    "documento": str(linha.get("documento", "")).strip(),
                })
    except Exception as e:
        print(f"Aviso: Não foi possível carregar {ARQUIVO_MOVIMENTOS}: {e}")

    return movimentos


def _salvar_movimentos_csv(caminho_csv: str, movimentos: list) -> None:
    """Grava o histórico de movimentações (Kardex) em data/movimentos.csv."""
    try:
        with open(caminho_csv, "w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUNAS_MOVIMENTOS)
            escritor.writeheader()
            for mov in movimentos:
                if not isinstance(mov, dict):
                    continue
                escritor.writerow({
                    "data": mov.get("data", ""),
                    "item": mov.get("item", ""),
                    "tipo": mov.get("tipo", ""),
                    "quantidade": mov.get("quantidade", 0.0),
                    "saldo": mov.get("saldo", 0.0),
                    "documento": mov.get("documento", ""),
                })
    except Exception as e:
        print(f"ERRO: Não foi possível salvar {ARQUIVO_MOVIMENTOS}: {e}")


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
        "movimentos": [],
    }

    arquivos = {
        "itens": "itens.json",
        "estrutura": "estrutura.json",
        "estoque": "estoque.json",
        "centros": "centros.json",
        "roteiros": "roteiros.json",
        "mps": "mps.json",
        "ordens": "ordens.json",
    }

    for chave, nome_arquivo in arquivos.items():
        caminho = os.path.join(DIRETORIO_DADOS, nome_arquivo)
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = json.load(f)
                if isinstance(conteudo, dict):
                    dados[chave] = conteudo
                else:
                    print(
                        f"Aviso: Estrutura inválida em {nome_arquivo} "
                        f"(esperado objeto/dicionário). Mantendo valor padrão."
                    )
            except Exception as e:
                print(f"Aviso: Não foi possível carregar {nome_arquivo}: {e}")

    caminho_movimentos = os.path.join(DIRETORIO_DADOS, ARQUIVO_MOVIMENTOS)
    movimentos_carregados = _carregar_movimentos_csv(caminho_movimentos)
    if isinstance(movimentos_carregados, list):
        dados["movimentos"] = movimentos_carregados
    else:
        print(
            f"Aviso: Estrutura inválida em {ARQUIVO_MOVIMENTOS} "
            f"(esperada lista). Mantendo histórico vazio."
        )

    return dados


def salvar_dados(dados: dict) -> None:
    """Salva todos os dicionários do sistema nos arquivos JSON da pasta data/ e o Kardex em CSV."""
    if not os.path.exists(DIRETORIO_DADOS):
        os.makedirs(DIRETORIO_DADOS)

    arquivos = {
        "itens": "itens.json",
        "estrutura": "estrutura.json",
        "estoque": "estoque.json",
        "centros": "centros.json",
        "roteiros": "roteiros.json",
        "mps": "mps.json",
        "ordens": "ordens.json",
    }

    for chave, nome_arquivo in arquivos.items():
        caminho = os.path.join(DIRETORIO_DADOS, nome_arquivo)
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados[chave], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ERRO: Não foi possível salvar {nome_arquivo}: {e}")

    caminho_movimentos = os.path.join(DIRETORIO_DADOS, ARQUIVO_MOVIMENTOS)
    _salvar_movimentos_csv(caminho_movimentos, dados.get("movimentos", []))
