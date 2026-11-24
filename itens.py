"""Módulo de cadastro, listagem e alteração de itens do Sistema MRP II (RF02, RN01)."""

from utils import (
    ler_codigo,
    ler_float,
    ler_inteiro,
    ler_texto_obrigatorio,
    normalizar_texto,
)

TIPOS_VALIDOS = {"PA": "Produto Acabado", "SA": "Semiacabado", "MP": "Matéria-Prima"}


def alterar_item(dados: dict) -> None:
    """Altera os dados editáveis de um item existente preservando código e tipo (RF02, RN01)."""
    print("\n--- ALTERAÇÃO DE ITEM ---")
    if not dados.get("itens"):
        print("ERRO: Nenhum item cadastrado para alterar.")
        return

    codigo = input("Digite o código do item que deseja alterar (ex: PA-001, MP-100): ").strip().upper()
    item = dados["itens"].get(codigo)
    if not item:
        print(f"ERRO: Item '{codigo}' não encontrado.")
        return

    print(f"Editando {codigo} [Tipo: {item['tipo']}] — deixe em branco para manter o valor atual.")

    nova_descricao = normalizar_texto(input(f"Descrição [{item['descricao']}]: "))
    if nova_descricao:
        item["descricao"] = nova_descricao

    nova_unidade = normalizar_texto(input(f"Unidade de medida [{item['unidade']}]: "))
    if nova_unidade:
        item["unidade"] = nova_unidade

    custo = ler_float(
        f"Custo unitário (R$) [{item['custo_unitario']:.2f}]: ",
        minimo=0.0,
        permitir_vazio=True,
        padrao=float(item["custo_unitario"]),
    )
    lt = ler_inteiro(
        f"Lead time (semanas) [{item['lead_time']}]: ",
        minimo=0,
        permitir_vazio=True,
        padrao=int(item["lead_time"]),
    )
    es = ler_float(
        f"Estoque de segurança [{item['estoque_seguranca']:.1f}]: ",
        minimo=0.0,
        permitir_vazio=True,
        padrao=float(item["estoque_seguranca"]),
    )
    lote = ler_float(
        f"Lote mínimo [{item['lote_minimo']:.1f}]: ",
        minimo=0.0,
        permitir_vazio=True,
        padrao=float(item["lote_minimo"]),
    )

    if None in (custo, lt, es, lote):
        print("ERRO: Valor numérico inválido. Alteração cancelada.")
        return

    item["custo_unitario"] = custo
    item["lead_time"] = lt
    item["estoque_seguranca"] = es
    item["lote_minimo"] = lote

    print(f"Sucesso: Item '{codigo}' atualizado!")


def validar_codigo_item(codigo: str) -> bool:
    """Valida se o código do item segue estritamente o formato Tipo-Número (ex: PA-001, SA-020)."""
    partes = codigo.strip().upper().split("-")
    if len(partes) != 2:
        return False
    tipo, num = partes[0], partes[1]
    return tipo in TIPOS_VALIDOS and num.isdigit()


def cadastrar_item(dados: dict) -> None:
    """Cadastra um novo item (PA, SA ou MP) no sistema (RF01, RN01, RNF04)."""
    print("\n--- CADASTRO DE ITEM ---")
    codigo = ler_codigo("Digite o código do item (ex: PA-001, SA-010, MP-201): ")
    if not validar_codigo_item(codigo):
        print("ERRO: Código inválido (RN01). Use o formato Tipo-Número (ex.: PA-001, SA-020, MP-201).")
        return
    if codigo in dados["itens"]:
        print(f"ERRO: O item {codigo} já está cadastrado no sistema.")
        return

    tipo = input(
        "Digite o tipo do item ([PA] Produto Acabado, [SA] Semi-acabado, [MP] Matéria-prima): "
    ).strip().upper()
    if tipo not in ["PA", "SA", "MP"]:
        print("ERRO: Tipo inválido. Escolha PA, SA ou MP.")
        return
    if not codigo.startswith(f"{tipo}-"):
        print(f"ERRO: O prefixo do código '{codigo}' não corresponde ao tipo '{tipo}'.")
        return

    descricao = ler_texto_obrigatorio("Digite a descrição do item: ", campo="descrição")
    unidade = ler_texto_obrigatorio("Unidade de medida (ex: un, m, L, kg): ", campo="unidade")

    custo_unitario = ler_float("Custo unitário (R$): ", minimo=0.0)
    lead_time = ler_inteiro("Lead time (em semanas): ", minimo=0)
    estoque_seguranca = ler_float("Estoque de segurança: ", minimo=0.0)
    lote_minimo = ler_float("Lote mínimo de compra/produção: ", minimo=0.0)

    if None in (custo_unitario, lead_time, estoque_seguranca, lote_minimo):
        print("ERRO: Valores numéricos inválidos inseridos. Operação cancelada.")
        return

    dados["itens"][codigo] = {
        "codigo": codigo,
        "tipo": tipo,
        "descricao": descricao,
        "unidade": unidade,
        "custo_unitario": custo_unitario,
        "lead_time": lead_time,
        "estoque_seguranca": estoque_seguranca,
        "lote_minimo": lote_minimo,
    }

    if codigo not in dados["estoque"]:
        dados["estoque"][codigo] = {"saldo_atual": 0.0}

    print(f"Sucesso: Item {codigo} ({descricao}) cadastrado com saldo inicial 0.0!")


def listar_itens(dados: dict) -> None:
    """Lista todos os itens cadastrados no sistema de forma organizada (RF02)."""
    print("\n--- LISTA DE ITENS CADASTRADOS ---")
    if not dados["itens"]:
        print("Nenhum item cadastrado até o momento.")
        return

    print(f"{'Código':<10} | {'Tipo':<5} | {'Descrição':<30} | {'Un':<4} | {'Custo (R$)':<10} | {'LT':<3} | {'Est.Seg':<8} | {'Lote Mín':<8}")
    print("-" * 95)
    for codigo, item in sorted(dados["itens"].items()):
        print(f"{codigo:<10} | {item['tipo']:<5} | {item['descricao']:<30} | {item['unidade']:<4} | {item['custo_unitario']:<10.2f} | {item['lead_time']:<3} | {item['estoque_seguranca']:<8.1f} | {item['lote_minimo']:<8.1f}")


def gerenciar_itens(dados: dict) -> None:
    """Submenu para gerenciamento de itens."""
    while True:
        print("\n--- GESTÃO DE ITENS ---")
        print("1. Cadastrar novo item")
        print("2. Listar itens cadastrados")
        print("3. Alterar item existente")
        print("0. Voltar ao menu anterior")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            cadastrar_item(dados)
        elif op == "2":
            listar_itens(dados)
        elif op == "3":
            alterar_item(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
