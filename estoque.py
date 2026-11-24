"""Módulo de controle de estoque, saldos e histórico (Kardex) (RF04, RF05, RN02, RN10)."""

from datetime import datetime
from utils import ler_codigo, ler_float, ler_inteiro, normalizar_texto


def movimentar_estoque(dados: dict) -> None:
    """Registra entrada, saída ou ajuste de estoque, atualizando saldo e kardex (RF04, RN02, RN10)."""
    print("\n--- MOVIMENTAÇÃO DE ESTOQUE ---")
    codigo = ler_codigo("Digite o código do item (ex: MP-202, SA-010): ")
    if codigo not in dados["itens"]:
        print(f"ERRO: Item {codigo} não cadastrado no sistema.")
        return

    tipo_mov = input("Tipo de movimentação - [E]ntrada, [S]aída, [A]juste: ").strip().upper()
    if tipo_mov not in ["E", "S", "A"]:
        print("ERRO: Tipo de movimentação inválido. Escolha E, S ou A.")
        return

    sigla_tipo = "ENTRADA" if tipo_mov == "E" else ("SAIDA" if tipo_mov == "S" else "AJUSTE")

    quantidade = ler_float("Quantidade: ", minimo=0.0001)
    if quantidade is None:
        print("ERRO: A quantidade deve ser maior que zero.")
        return
    
    documento = normalizar_texto(
        input("Documento de origem ou motivo (ex: NF 4521, OP-0003, Inventário): ")
    )
    if not documento:
        documento = "Movimentação manual"

    data_atual = datetime.now().strftime("%d/%m/%Y")

    # Garante que o item possui registro de estoque
    if codigo not in dados["estoque"]:
        dados["estoque"][codigo] = {"saldo_atual": 0.0}

    saldo_atual = dados["estoque"][codigo]["saldo_atual"]

    # Cálculo do novo saldo conforme o tipo
    if sigla_tipo == "ENTRADA":
        novo_saldo = saldo_atual + quantidade
    elif sigla_tipo == "SAIDA":
        if quantidade > saldo_atual:
            print(f"ERRO: saldo insuficiente (saldo atual: {saldo_atual:.1f} un). Operação cancelada. (RN02)")
            return
        novo_saldo = saldo_atual - quantidade
    else:  # AJUSTE
        sinal_ajuste = ler_inteiro(
            "O ajuste é positivo (1) ou negativo (-1)? Digite 1 ou -1: ",
            minimo=-1,
            maximo=1,
        )
        while sinal_ajuste == 0:
            print("Erro: digite apenas 1 ou -1.")
            sinal_ajuste = ler_inteiro(
                "O ajuste é positivo (1) ou negativo (-1)? Digite 1 ou -1: ",
                minimo=-1,
                maximo=1,
            )
        delta = quantidade * sinal_ajuste
        if saldo_atual + delta < 0:
            print(f"ERRO: O ajuste deixaria o saldo negativo ({saldo_atual + delta:.1f}). Operação cancelada. (RN02)")
            return
        novo_saldo = saldo_atual + delta
        quantidade = delta

    # Atualiza o saldo no dicionário
    dados["estoque"][codigo]["saldo_atual"] = novo_saldo

    # Registra no Kardex (lista de movimentos globais)
    movimento = {
        "data": data_atual,
        "item": codigo,
        "tipo": sigla_tipo,
        "quantidade": quantidade if sigla_tipo != "SAIDA" else -quantidade,
        "saldo": novo_saldo,
        "documento": documento
    }
    dados["movimentos"].append(movimento)

    print(f"Sucesso: Movimentação registrada! Novo saldo de {codigo}: {novo_saldo:.1f} {dados['itens'][codigo]['unidade']}")


def consultar_kardex(dados: dict) -> None:
    """Consulta o saldo atual e o extrato (Kardex) de um item, alertando estoque de segurança (RF05)."""
    print("\n--- CONSULTA DE KARDEX E SALDO ---")
    codigo = ler_codigo("Digite o código do item (ex: MP-202, PA-001): ")
    
    if codigo not in dados["itens"]:
        print(f"ERRO: Item {codigo} não cadastrado.")
        return

    item = dados["itens"][codigo]
    estoque_info = dados["estoque"].get(codigo, {"saldo_atual": 0.0})
    saldo = estoque_info["saldo_atual"]
    est_seg = item["estoque_seguranca"]

    print(f"\nKARDEX - {codigo} {item['descricao']} ({item['unidade']})")
    print(f"Saldo Atual: {saldo:.1f} | Estoque de Segurança: {est_seg:.1f}")
    print("-" * 75)
    print(f"{'Data':<12} | {'Tipo':<10} | {'Qtde':<8} | {'Saldo':<8} | {'Documento':<30}")
    print("-" * 75)

    encontrou_mov = False
    for mov in dados["movimentos"]:
        if mov["item"] == codigo:
            encontrou_mov = True
            print(f"{mov['data']:<12} | {mov['tipo']:<10} | {mov['quantidade']:<+8.1f} | {mov['saldo']:<8.1f} | {mov['documento']:<30}")

    if not encontrou_mov:
        print("Nenhuma movimentação registrada para este item.")

    print("-" * 75)
    # Alerta de estoque de segurança (RF05)
    if saldo < est_seg:
        print(f"ALERTA: saldo ({saldo:.1f} un) abaixo do estoque de segurança ({est_seg:.1f} un)!")


def gerenciar_estoque(dados: dict) -> None:
    """Submenu para gestão de estoque e kardex."""
    while True:
        print("\n--- GESTÃO DE ESTOQUE E KARDEX ---")
        print("1. Movimentar estoque (Entrada, Saída, Ajuste)")
        print("2. Consultar Kardex e Saldo de um item")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            movimentar_estoque(dados)
        elif op == "2":
            consultar_kardex(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
