"""Módulo de Gestão de Estoque, Movimentações e Kardex."""
import os
import csv
from datetime import datetime
from persistencia import carregar_json, salvar_json
from utils import ler_inteiro, pausar

CAMINHO_MOVIMENTOS = "data/movimentos.csv"

def garantir_csv_movimentos():
    """Garante que o arquivo CSV de movimentações existe com cabeçalho."""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(CAMINHO_MOVIMENTOS):
        with open(CAMINHO_MOVIMENTOS, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["data", "codigo_item", "tipo", "quantidade", "documento"])

def gerenciar_estoque():
    """Menu para gerenciar estoques e kardex."""
    while True:
        print("\n--- GESTÃO DE ESTOQUE ---")
        print("1. Registrar Movimentação (Entrada, Saída, Ajuste)")
        print("2. Consultar Saldo e Kardex de um Item")
        print("0. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            registrar_movimentacao()
        elif opcao == "2":
            consultar_kardex()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

def calcular_saldo_atual(codigo_item: str) -> int:
    """Calcula o saldo atual de um item somando todas as movimentações do Kardex."""
    garantir_csv_movimentos()
    saldo = 0
    with open(CAMINHO_MOVIMENTOS, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["codigo_item"] == codigo_item:
                tipo = row["tipo"]
                qtd = int(row["quantidade"])
                if tipo == "ENTRADA":
                    saldo += qtd
                elif tipo == "SAIDA":
                    saldo -= qtd
                elif tipo == "AJUSTE":
                    # No ajuste, a quantidade pode ser positiva ou negativa dependendo do lançamento
                    saldo += qtd
    return saldo

def registrar_movimentacao():
    """Registra uma entrada, saída ou ajuste de estoque (RF04, RN02)."""
    garantir_csv_movimentos()
    itens = carregar_json("itens.json")
    
    codigo = input("Código do item: ").strip()
    if codigo not in itens:
        print(f"ERRO: Item {codigo} não encontrado.")
        pausar()
        return
        
    print("Tipo de movimentação:")
    print("[E]ntrada | [S]aida | [A]juste")
    tipo_input = input("Escolha (E/S/A): ").upper()
    
    if tipo_input == "E":
        tipo = "ENTRADA"
    elif tipo_input == "S":
        tipo = "SAIDA"
    elif tipo_input == "A":
        tipo = "AJUSTE"
    else:
        print("ERRO: Tipo inválido.")
        pausar()
        return
        
    quantidade = ler_inteiro("Quantidade: ")
    documento = input("Documento/Motivo (ex: NF 4521, Inventário mensal): ").strip()
    
    # Validação de saldo negativo para saídas (RN02)
    if tipo == "SAIDA":
        saldo_atual = calcular_saldo_atual(codigo)
        if quantidade > saldo_atual:
            print(f"ERRO: Saldo insuficiente (saldo atual: {saldo_atual} un). Operação cancelada.")
            pausar()
            return

    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    with open(CAMINHO_MOVIMENTOS, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Se for ajuste, permitimos valor positivo/negativo conforme entrada do usuário
        writer.writerow([data_atual, codigo, tipo, quantidade, documento])
        
    print("Sucesso: Movimentação registrada!")
    pausar()

def consultar_kardex():
    """Consulta o saldo, histórico (kardex) e alerta de estoque de segurança (RF05)."""
    garantir_csv_movimentos()
    itens = carregar_json("itens.json")
    
    codigo = input("Digite o código do item para consulta: ").strip()
    if codigo not in itens:
        print(f"ERRO: Item {codigo} não encontrado.")
        pausar()
        return
        
    item = itens[codigo]
    saldo = calcular_saldo_atual(codigo)
    
    print(f"\nKARDEX - {codigo} {item['descricao']} ({item['unidade']})")
    print(f"{'Data':<10} | {'Tipo':<8} | {'Qtde':<6} | {'Documento'}")
    print("-" * 55)
    
    with open(CAMINHO_MOVIMENTOS, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["codigo_item"] == codigo:
                sinal = "+" if row["tipo"] == "ENTRADA" else ("" if row["tipo"] == "AJUSTE" else "-")
                qtde_str = f"{sinal}{row['quantidade']}"
                print(f"{row['data']:<10} | {row['tipo']:<8} | {qtde_str:<6} | {row['documento']}")
                
    print("-" * 55)
    print(f"Estoque atual: {saldo} {item['unidade']}"   )
    
    if saldo < item["estoque_seguranca"]:
        print(f"ALERTA: Saldo ({saldo} un) abaixo do estoque de segurança ({item['estoque_seguranca']} un).")
    pausar()