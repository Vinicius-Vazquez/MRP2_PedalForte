"""Módulo de cálculo do MRP (Material Requirements Planning) por explosão de necessidades (RF08, RF09, RN04, RN05, RN06)."""

HORIZONTE_SEMANAS = 8

def executar_calculo_mrp(dados: dict) -> None:
    """Executa o planejamento de necessidades de materiais para todos os níveis (PA, SA, MP) (RF08, RF09)."""
    print("\n--- EXECUTANDO CÁLCULO MRP ---")
    
    if not dados["mps"]:
        print("ERRO: Nenhum dado de MPS cadastrado para iniciar o cálculo.")
        return

    # Estrutura auxiliar para acumular as necessidades brutas de cada item ao longo das 8 semanas
    necessidades_brutas = {cod: [0.0] * HORIZONTE_SEMANAS for cod in dados["itens"]}
    
    # 1. Carrega a demanda do MPS para os Produtos Acabados (PA)
    for pa, demandas in dados["mps"].items():
        if pa in necessidades_brutas:
            for s in range(min(len(demandas), HORIZONTE_SEMANAS)):
                necessidades_brutas[pa][s] += demandas[s]

    # 2. Explosão de necessidades através da Estrutura de Produto (BOM) em cascata de níveis
    # Ordenamos ou iteramos garantindo que PAs geram demandas para SAs, e SAs para MPs.
    # Como temos no máximo 3 níveis (PA -> SA -> MP), podemos fazer duas varreduras de explosão.
    
    # Nível 1 para Nível 2 (PA -> Componentes diretos)
    for pai, comps in dados["estrutura"].items():
        if pai in necessidades_brutas:
            for semana in range(HORIZONTE_SEMANAS):
                qtd_pai_nec = necessidades_brutas[pai][semana]
                if qtd_pai_nec > 0:
                    for comp in comps:
                        filho = comp["componente"]
                        proporcao = comp["quantidade"]
                        if filho in necessidades_brutas:
                            necessidades_brutas[filho][semana] += qtd_pai_nec * proporcao

    # Nível 2 para Nível 3 (SA -> Matérias-Primas)
    # Varredura extra caso um SA tenha filhos que sejam MPs ou outros componentes
    for _ in range(2):
        for pai, comps in dados["estrutura"].items():
            if pai in necessidades_brutas:
                for semana in range(HORIZONTE_SEMANAS):
                    qtd_pai_nec = necessidades_brutas[pai][semana]
                    if qtd_pai_nec > 0:
                        for comp in comps:
                            filho = comp["componente"]
                            proporcao = comp["quantidade"]
                            if filho in necessidades_brutas:
                                necessidades_brutas[filho][semana] += qtd_pai_nec * proporcao

    # 3. Processamento do MRP por item (Necessidade Líquida, Lote Mínimo e Lead Time Offset)
    resultados_mrp = {}

    print("\n" + "=" * 90)
    print(" RELATÓRIO DE PLANEJAMENTO MRP (NECESSIDADES LÍQUIDAS E ORDENS PLANEJADAS) ")
    print("=" * 90)

    for codigo, item in sorted(dados["itens"].items()):
        lead_time = item["lead_time"]
        est_seg = item["estoque_seguranca"]
        lote_min = item["lote_minimo"]
        
        # Saldo inicial disponível no estoque físico
        estoque_info = dados["estoque"].get(codigo, {"saldo_atual": 0.0})
        saldo_projetado = estoque_info["saldo_atual"]

        brutas = necessidades_brutas[codigo]
        liquidas = [0.0] * HORIZONTE_SEMANAS
        liberacao_ordens = [0.0] * HORIZONTE_SEMANAS

        for s in range(HORIZONTE_SEMANAS):
            nec_bruta = brutas[s]
            
            # Necessidade Líquida = (Necessidade Bruta + Estoque de Segurança) - Saldo Projetado Anterior
            # Se o saldo cobrir a necessidade bruta + segurança, necessidade líquida é 0.
            necessidade_total = nec_bruta + est_seg
            if necessidade_total > saldo_projetado:
                liq = necessidade_total - saldo_projetado
            else:
                liq = 0.0

            liquidas[s] = liq

            # Aplicação de Lote Mínimo (Loteação)
            if liq > 0:
                if lote_min > 0 and liq < lote_min:
                    lote_producao = lote_min
                else:
                    lote_producao = liq # Poderia aplicar múltiplos de lote se necessário
            else:
                lote_producao = 0.0

            # Atualiza o saldo projetado para a próxima semana
            saldo_projetado = max(0.0, saldo_projetado - nec_bruta) + lote_producao

            # Lead Time Offset (Atraso de liberação de ordem baseado no lead time em semanas)
            if lote_producao > 0:
                semana_liberacao = s - lead_time
                if semana_liberacao >= 0:
                    liberacao_ordens[semana_liberacao] += lote_producao
                else:
                    # Necessidade já no horizonte passado ou imediato (atraso / backlog)
                    liberacao_ordens[0] += lote_producao

        resultados_mrp[codigo] = {
            "brutas": brutas,
            "liquidas": liquidas,
            "liberacao": liberacao_ordens
        }

        # Exibição resumida no console para o item se houver alguma demanda ou ordem
        if sum(brutas) > 0 or sum(liberacao_ordens) > 0:
            print(f"\nItem: {codigo} - {item['descricao']} (LT: {lead_time} sem | Est.Seg: {est_seg} | Lote Mín: {lote_min})")
            print(f"  Semana        | " + " | ".join([f"S{i}" for i in range(1, HORIZONTE_SEMANAS + 1)]))
            print("  " + "-" * 70)
            print(f"  Nec. Brutas   | " + " | ".join([f"{int(x):<4}" for x in brutas]))
            print(f"  Nec. Líquidas | " + " | ".join([f"{int(x):<4}" for x in liquidas]))
            print(f"  Ordens Plan.  | " + " | ".join([f"{int(x):<4}" for x in liberacao_ordens]))

    print("\n" + "=" * 90)
    print("Cálculo MRP concluído com sucesso!")
    
    # Armazena os resultados no dicionário global para uso posterior em ordens e relatórios
    dados["mrp_calculado"] = resultados_mrp