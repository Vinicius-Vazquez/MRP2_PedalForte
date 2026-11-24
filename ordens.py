"""Módulo de geração, consulta e gestão de Ordens de Produção (OP) e Ordens de Compra (OC) (RF09-RF11, RN02, RN07-RN10)."""

from datetime import datetime
from utils import iterar_componentes, ler_codigo

HORIZONTE_SEMANAS = 8


def _garantir_estrutura_ordens(dados: dict) -> dict:
    """Garante que dados['ordens'] seja um dicionário."""
    if "ordens" not in dados or not isinstance(dados["ordens"], dict):
        dados["ordens"] = {}
    return dados["ordens"]


def _proximo_codigo_ordem(ordens: dict, prefixo: str) -> str:
    """Gera o próximo código sequencial (ex.: OP-001, OC-001) sem colisão."""
    maior_num = 0
    for cod in ordens:
        if isinstance(cod, str) and cod.startswith(f"{prefixo}-"):
            parte_num = cod.split("-", 1)[1]
            if parte_num.isdigit():
                maior_num = max(maior_num, int(parte_num))
    return f"{prefixo}-{maior_num + 1:03d}"


def _registrar_movimento_kardex(
    dados: dict,
    codigo_item: str,
    tipo_mov: str,
    quantidade: float,
    saldo_apos: float,
    documento: str,
) -> None:
    """Registra movimentação no histórico/kardex em dados['movimentos'] (RN10)."""
    movimentos = dados.get("movimentos")
    if not isinstance(movimentos, list):
        movimentos = []
        dados["movimentos"] = movimentos

    movimentos.append({
        "data": datetime.now().strftime("%d/%m/%Y"),
        "item": codigo_item,
        "tipo": tipo_mov,
        "quantidade": quantidade,
        "saldo": saldo_apos,
        "documento": documento,
    })


def gerar_ordens_automaticas(dados: dict) -> None:
    """Gera OPs e OCs planejadas a partir das liberações planejadas do MRP (RF09, RN07, RN08)."""
    print("\n--- GERAÇÃO DE ORDENS (MRP -> OP / OC) ---")

    mrp_calc = dados.get("mrp_calculado")
    if not isinstance(mrp_calc, dict) or not mrp_calc:
        print("ERRO: Execute o cálculo MRP (Opção 4) antes de gerar as ordens.")
        return

    ordens = _garantir_estrutura_ordens(dados)
    itens = dados.get("itens", {})

    # RN07 / RN08: Remove ordens PLANEJADAS e ATRASADAS anteriores antes de gerar as novas
    status_removidos = {"PLANEJADA", "ATRASADA"}
    for cod in [
        k
        for k, v in ordens.items()
        if isinstance(v, dict) and str(v.get("status", "")).upper() in status_removidos
    ]:
        del ordens[cod]

    novas_geradas = 0
    excecoes = 0

    for codigo, resultado in sorted(mrp_calc.items()):
        if codigo not in itens or not isinstance(resultado, dict):
            continue
        liberacao = resultado.get("liberacao", [])
        atrasos = resultado.get("atrasos", [])
        tipo_item = str(itens[codigo].get("tipo", "")).upper()
        lead_time = int(itens[codigo].get("lead_time", 0))

        for idx_sem, qtd in enumerate(liberacao):
            qtd_float = float(qtd)
            if qtd_float > 0:
                semana_liberacao = idx_sem + 1
                semana_entrega = semana_liberacao + lead_time

                if tipo_item in {"PA", "SA"}:
                    num_ordem = _proximo_codigo_ordem(ordens, "OP")
                    tipo_ordem = "OP"
                else:
                    num_ordem = _proximo_codigo_ordem(ordens, "OC")
                    tipo_ordem = "OC"

                # RN07: Marca como ATRASADA se a liberação cairia antes da semana 1
                atrasada = bool(atrasos[idx_sem]) if idx_sem < len(atrasos) else False
                status_inicial = "ATRASADA" if atrasada else "PLANEJADA"
                if atrasada:
                    excecoes += 1
                    print(f"EXCEÇÃO: Ordem {num_ordem} ({codigo}) marcada como ATRASADA (liberação antes da S1).")

                ordens[num_ordem] = {
                    "codigo_ordem": num_ordem,
                    "tipo": tipo_ordem,
                    "item": codigo,
                    "quantidade": qtd_float,
                    "semana": semana_liberacao,
                    "semana_liberacao": semana_liberacao,
                    "semana_entrega": semana_entrega,
                    "status": status_inicial,
                }
                novas_geradas += 1

    print(f"Sucesso: {novas_geradas} ordens geradas a partir do MRP.")
    if excecoes:
        print(f"Atenção: {excecoes} ordem(ns) sinalizada(s) como ATRASADA (RN07).")


def listar_ordens(dados: dict) -> None:
    """Lista todas as Ordens de Produção e de Compra cadastradas no sistema (RF09, RF10)."""
    print("\n--- LISTA DE ORDENS DE PRODUÇÃO E COMPRA ---")

    ordens = dados.get("ordens", {})
    if not isinstance(ordens, dict) or not ordens:
        print("Nenhuma ordem cadastrada ou gerada até o momento.")
        return

    print(f"{'Ordem':<10} | {'Tipo':<5} | {'Item':<10} | {'Qtde':<10} | {'Lib.':<5} | {'Entr.':<5} | {'Status':<12}")
    print("-" * 76)
    for num_ordem, ord_info in sorted(ordens.items()):
        if not isinstance(ord_info, dict):
            continue
        sem_lib = ord_info.get("semana_liberacao", ord_info.get("semana", "-"))
        sem_ent = ord_info.get("semana_entrega", "-")
        print(
            f"{num_ordem:<10} | {str(ord_info.get('tipo', '')):<5} | "
            f"{str(ord_info.get('item', '')):<10} | {float(ord_info.get('quantidade', 0.0)):<10.1f} | "
            f"{str(sem_lib):<5} | {str(sem_ent):<5} | {str(ord_info.get('status', '')):<12}"
        )


def _alterar_status_ordem(dados: dict, status_esperado: str, novo_status: str, acao_label: str) -> None:
    """Transiciona o status de uma ordem validando o estado atual (RF10)."""
    ordens = dados.get("ordens", {})
    if not isinstance(ordens, dict) or not ordens:
        print("ERRO: Não há ordens cadastradas.")
        return

    cod = ler_codigo(f"Código da ordem para {acao_label} (ex.: OP-001 ou OC-001): ")
    ordem = ordens.get(cod)
    if not isinstance(ordem, dict):
        print(f"ERRO: Ordem '{cod}' não encontrada.")
        return

    status_atual = str(ordem.get("status", "")).upper()
    if status_atual != status_esperado:
        print(
            f"ERRO: Não é possível {acao_label} a ordem '{cod}' com status '{status_atual}'. "
            f"Status exigido: '{status_esperado}'."
        )
        return

    ordem["status"] = novo_status
    print(f"Sucesso: Ordem '{cod}' atualizada de '{status_esperado}' para '{novo_status}'.")


def firmar_ordem(dados: dict) -> None:
    """Muda ordem de PLANEJADA para FIRME (RF10)."""
    _alterar_status_ordem(dados, "PLANEJADA", "FIRME", "firmar")


def liberar_ordem(dados: dict) -> None:
    """Muda ordem de FIRME para LIBERADA (RF10)."""
    _alterar_status_ordem(dados, "FIRME", "LIBERADA", "liberar")


def encerrar_ordem(dados: dict) -> None:
    """Encerra manualmente uma ordem LIBERADA (RF10)."""
    _alterar_status_ordem(dados, "LIBERADA", "ENCERRADA", "encerrar")


def apontar_producao(dados: dict) -> None:
    """Aponta produção de OP LIBERADA: valida/baixa componentes, entra item e encerra OP (RF11, RN02, RN10)."""
    print("\n--- APONTAMENTO DE PRODUÇÃO (OP LIBERADA) ---")
    ordens = dados.get("ordens", {})
    if not isinstance(ordens, dict) or not ordens:
        print("ERRO: Não há ordens cadastradas.")
        return

    cod_op = ler_codigo("Código da OP para apontar (ex.: OP-001): ")
    ordem = ordens.get(cod_op)
    if not isinstance(ordem, dict):
        print(f"ERRO: Ordem '{cod_op}' não encontrada.")
        return

    if str(ordem.get("tipo", "")).upper() != "OP":
        print(f"ERRO: '{cod_op}' não é uma Ordem de Produção (OP).")
        return

    if str(ordem.get("status", "")).upper() != "LIBERADA":
        print(f"ERRO: Apenas OPs com status 'LIBERADA' podem ser apontadas (atual: '{ordem.get('status')}').")
        return

    item_pai = str(ordem.get("item", ""))
    qtd_op = float(ordem.get("quantidade", 0.0))
    if qtd_op <= 0:
        print("ERRO: Quantidade da OP inválida.")
        return

    estoque = dados.setdefault("estoque", {})
    estrutura_pai = dados.get("estrutura", {}).get(item_pai)
    componentes = iterar_componentes(estrutura_pai)

    # 1. Verifica disponibilidade de todos os componentes antes de alterar qualquer saldo (RN02)
    faltantes: list[str] = []
    consumos_necessarios: list[tuple[str, float]] = []
    for comp_cod, qtd_unit in componentes:
        nec_total = qtd_op * qtd_unit
        saldo_comp = float(estoque.get(comp_cod, {}).get("saldo_atual", 0.0))
        if saldo_comp < nec_total:
            faltantes.append(f"{comp_cod} (necessário: {nec_total:.2f}, disponível: {saldo_comp:.2f})")
        else:
            consumos_necessarios.append((comp_cod, nec_total))

    if faltantes:
        print("ERRO: Apontamento rejeitado por falta de componente(s) em estoque (RN02):")
        for f in faltantes:
            print(f"  - {f}")
        return

    # 2. Baixa os componentes do estoque e registra no histórico/kardex
    for comp_cod, nec_total in consumos_necessarios:
        info_comp = estoque.setdefault(comp_cod, {"saldo_atual": 0.0})
        novo_saldo_comp = float(info_comp.get("saldo_atual", 0.0)) - nec_total
        info_comp["saldo_atual"] = novo_saldo_comp
        _registrar_movimento_kardex(
            dados,
            codigo_item=comp_cod,
            tipo_mov="SAIDA",
            quantidade=-nec_total,
            saldo_apos=novo_saldo_comp,
            documento=f"Apontamento {cod_op} ({item_pai})",
        )

    # 3. Dá entrada do item produzido no estoque
    info_pai = estoque.setdefault(item_pai, {"saldo_atual": 0.0})
    novo_saldo_pai = float(info_pai.get("saldo_atual", 0.0)) + qtd_op
    info_pai["saldo_atual"] = novo_saldo_pai
    _registrar_movimento_kardex(
        dados,
        codigo_item=item_pai,
        tipo_mov="ENTRADA",
        quantidade=qtd_op,
        saldo_apos=novo_saldo_pai,
        documento=f"Apontamento {cod_op}",
    )

    # 4. Encerra a OP
    ordem["status"] = "ENCERRADA"
    print(f"Sucesso: OP '{cod_op}' apontada (+{qtd_op:.2f} de {item_pai}) e encerrada.")


def gerenciar_ordens(dados: dict) -> None:
    """Submenu para gestão de ordens (geração, listagem, ciclo de status e apontamento)."""
    while True:
        print("\n--- GESTÃO DE ORDENS DE PRODUÇÃO E COMPRA ---")
        print("1. Gerar ordens automaticamente a partir do MRP")
        print("2. Listar todas as ordens (OP / OC)")
        print("3. Firmar ordem (PLANEJADA -> FIRME)")
        print("4. Liberar ordem (FIRME -> LIBERADA)")
        print("5. Encerrar ordem (LIBERADA -> ENCERRADA)")
        print("6. Apontar produção de OP liberada")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            gerar_ordens_automaticas(dados)
        elif op == "2":
            listar_ordens(dados)
        elif op == "3":
            firmar_ordem(dados)
        elif op == "4":
            liberar_ordem(dados)
        elif op == "5":
            encerrar_ordem(dados)
        elif op == "6":
            apontar_producao(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
