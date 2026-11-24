"""Módulo de cálculo do MRP (Material Requirements Planning) por explosão de necessidades (RF08, RF09, RN04-RN08)."""

from utils import iterar_componentes

HORIZONTE_SEMANAS = 8


def _iterar_componentes(estrutura_pai) -> list[tuple[str, float]]:
    """Normaliza os componentes de um item pai como pares (codigo_filho, quantidade)."""
    if isinstance(estrutura_pai, dict):
        return [(str(filho), float(qtd)) for filho, qtd in estrutura_pai.items()]
    if isinstance(estrutura_pai, list):
        pares: list[tuple[str, float]] = []
        for comp in estrutura_pai:
            if isinstance(comp, dict) and "componente" in comp and "quantidade" in comp:
                pares.append((str(comp["componente"]), float(comp["quantidade"])))
        return pares
    return []


def _explodir_necessidades(
    necessidades_brutas: dict[str, list[float]],
    dados: dict,
    tipos_origem: set[str],
    tipos_destino_permitidos: set[str],
) -> None:
    """Propaga necessidades brutas dos itens de origem para componentes permitidos na BOM."""
    itens = dados.get("itens", {})
    estrutura = dados.get("estrutura", {})

    for pai, comps in estrutura.items():
        if pai not in necessidades_brutas or pai not in itens:
            continue
        if itens[pai].get("tipo") not in tipos_origem:
            continue

        for semana in range(HORIZONTE_SEMANAS):
            qtd_pai_nec = necessidades_brutas[pai][semana]
            if qtd_pai_nec > 0:
                for filho, proporcao in iterar_componentes(comps):
                    if filho in necessidades_brutas and filho in itens:
                        if itens[filho].get("tipo") in tipos_destino_permitidos:
                            necessidades_brutas[filho][semana] += qtd_pai_nec * proporcao


def _recebimentos_programados_por_item(dados: dict) -> dict[str, list[float]]:
    """Soma quantidades de ordens FIRMES ou LIBERADAS por item e semana de entrega (RN08)."""
    itens = dados.get("itens", {})
    rp_por_item = {cod: [0.0] * HORIZONTE_SEMANAS for cod in itens}
    ordens = dados.get("ordens", {})
    lista_ordens = ordens.values() if isinstance(ordens, dict) else ordens

    for ordem in lista_ordens:
        if not isinstance(ordem, dict):
            continue
        status = str(ordem.get("status", "")).upper()
        if status in {"FIRME", "LIBERADA"}:
            cod_item = str(ordem.get("item", ""))
            qtd = float(ordem.get("quantidade", 0.0))
            sem_entrega = ordem.get("semana_entrega")
            if sem_entrega is None:
                lt = int(itens.get(cod_item, {}).get("lead_time", 0))
                sem_entrega = int(ordem.get("semana", 0)) + lt
            semana = int(sem_entrega)
            if cod_item in rp_por_item and 1 <= semana <= HORIZONTE_SEMANAS and qtd > 0:
                rp_por_item[cod_item][semana - 1] += qtd

    return rp_por_item


def _limpar_ordens_planejadas(dados: dict) -> None:
    """Remove ordens com status PLANEJADA ou ATRASADA antes de recalcular o MRP (RN07, RN08)."""
    ordens = dados.get("ordens")
    if isinstance(ordens, dict):
        status_removidos = {"PLANEJADA", "ATRASADA"}
        dados["ordens"] = {
            cod: info
            for cod, info in ordens.items()
            if isinstance(info, dict) and str(info.get("status", "")).upper() not in status_removidos
        }


def executar_calculo_mrp(dados: dict) -> None:
    """Executa o cálculo MRP na ordem PA -> SA -> MP (RF08, RF09, RN04-RN08)."""
    print("\n--- EXECUTANDO CÁLCULO MRP ---")

    mps = dados.get("mps", {})
    itens = dados.get("itens", {})
    if not mps:
        print("ERRO: Nenhum dado de MPS cadastrado para iniciar o cálculo.")
        return
    if not itens:
        print("ERRO: Nenhum item cadastrado.")
        return

    # RN08: Ordens PLANEJADAS são apagadas e recalculadas a cada execução do MRP
    _limpar_ordens_planejadas(dados)

    rp_por_item = _recebimentos_programados_por_item(dados)
    necessidades_brutas = {cod: [0.0] * HORIZONTE_SEMANAS for cod in itens}

    # 1. Demanda do MPS para Produtos Acabados (PA)
    for pa, demandas in mps.items():
        if pa in necessidades_brutas and isinstance(demandas, (list, tuple)):
            for s in range(min(len(demandas), HORIZONTE_SEMANAS)):
                necessidades_brutas[pa][s] += float(demandas[s])

    # 2. Explosão hierárquica explícita: primeiro PA -> SA/MP, depois SA -> MP (RN03, RN04)
    _explodir_necessidades(necessidades_brutas, dados, {"PA"}, {"SA", "MP"})
    _explodir_necessidades(necessidades_brutas, dados, {"SA"}, {"MP"})

    resultados_mrp = {}
    excecoes_atraso: list[str] = []

    print("\n" + "=" * 95)
    print(" RELATÓRIO DE PLANEJAMENTO MRP (8 SEMANAS) ")
    print("=" * 95)

    for codigo, item in sorted(itens.items()):
        lead_time = int(item.get("lead_time", 0))
        est_seg = float(item.get("estoque_seguranca", 0.0))
        lote_min = float(item.get("lote_minimo", 0.0))

        estoque_info = dados.get("estoque", {}).get(codigo, {"saldo_atual": 0.0})
        ep_anterior = float(estoque_info.get("saldo_atual", 0.0))

        brutas = necessidades_brutas[codigo]
        receb_prog = rp_por_item[codigo]
        liquidas = [0.0] * HORIZONTE_SEMANAS
        receb_plan = [0.0] * HORIZONTE_SEMANAS
        estoque_proj = [0.0] * HORIZONTE_SEMANAS
        liberacao_ordens = [0.0] * HORIZONTE_SEMANAS
        atrasos_semana = [False] * HORIZONTE_SEMANAS

        for s in range(HORIZONTE_SEMANAS):
            nb = brutas[s]
            rp = receb_prog[s]

            # RN05: NL(t) = max(0, NB(t) + ES - (EP(t-1) + RP(t)))
            nl = max(0.0, nb + est_seg - (ep_anterior + rp))
            liquidas[s] = nl

            # RN06: Recebimento planejado = max(NL, lote_minimo) quando há NL > 0
            if nl > 0:
                lote_producao = max(nl, lote_min) if lote_min > 0 else nl
            else:
                lote_producao = 0.0
            receb_plan[s] = lote_producao

            # Estoque projetado da semana t: EP(t) = EP(t-1) + RP(t) + RecebPlan(t) - NB(t)
            ep_atual = ep_anterior + rp + lote_producao - nb
            estoque_proj[s] = ep_atual
            ep_anterior = ep_atual

            # RN07: Liberação ocorre na semana do recebimento menos o lead time
            if lote_producao > 0:
                sem_lib_idx = s - lead_time
                if sem_lib_idx < 0:
                    atrasos_semana[s] = True
                    liberacao_ordens[0] += lote_producao
                    msg = (
                        f"EXCEÇÃO [ATRASADA]: {codigo} ({item.get('descricao', '')}) - "
                        f"recebimento na S{s + 1} com LT={lead_time} exige liberação antes da S1."
                    )
                    excecoes_atraso.append(msg)
                else:
                    liberacao_ordens[sem_lib_idx] += lote_producao

        resultados_mrp[codigo] = {
            "brutas": brutas,
            "recebimentos_programados": receb_prog,
            "estoque_projetado": estoque_proj,
            "liquidas": liquidas,
            "recebimentos_planejados": receb_plan,
            "liberacao": liberacao_ordens,
            "atrasos": atrasos_semana,
        }

        if sum(brutas) > 0 or sum(liberacao_ordens) > 0 or sum(receb_prog) > 0:
            print(
                f"\nItem: {codigo} - {item.get('descricao', '')} "
                f"(LT: {lead_time} sem | Est.Seg: {est_seg} | Lote Mín: {lote_min})"
            )
            print("  Semana        | " + " | ".join([f"S{i:<4}" for i in range(1, HORIZONTE_SEMANAS + 1)]))
            print("  " + "-" * 78)
            print("  Nec. Brutas   | " + " | ".join([f"{x:<5.1f}" for x in brutas]))
            print("  Rec. Progr.   | " + " | ".join([f"{x:<5.1f}" for x in receb_prog]))
            print("  Est. Projet.  | " + " | ".join([f"{x:<5.1f}" for x in estoque_proj]))
            print("  Nec. Líquidas | " + " | ".join([f"{x:<5.1f}" for x in liquidas]))
            print("  Rec. Plan.    | " + " | ".join([f"{x:<5.1f}" for x in receb_plan]))
            print("  Lib. Plan.    | " + " | ".join([f"{x:<5.1f}" for x in liberacao_ordens]))

    dados["mrp_calculado"] = resultados_mrp

    print("\n" + "=" * 95)
    print("Cálculo MRP concluído com sucesso!")
    if excecoes_atraso:
        print("\n--- MENSAGENS DE EXCEÇÃO (RN07) ---")
        for exc in excecoes_atraso:
            print(exc)
