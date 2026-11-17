"""Módulo responsável pela persistência de dados em arquivos JSON e CSV."""

def carregar_dados() -> dict:
    """Carrega todos os arquivos da pasta data/ para um dicionário central."""
    return {
        "itens": {}, "estrutura": {}, "estoque": {}, "movimentos": [],
        "centros": {}, "roteiros": {}, "mps": {}, "ordens": {}
    }

def salvar_dados(dados: dict) -> None:
    """Salva o estado atual dos dados nos arquivos correspondentes."""
    pass