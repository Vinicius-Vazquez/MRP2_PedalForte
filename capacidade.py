"""Módulo de cálculo e análise de Carga x Capacidade (CRP) dos Centros de Trabalho (RF12)."""

HORIZONTE_SEMANAS = 8

def analisar_capacidade(dados: dict) -> None:
    """Calcula a carga alocada em cada centro de trabalho por semana e compara com a capacidade disponível (RF12)."""
    print("\n--- ANÁLISE DE CARGA X CAPACIDADE (CRP) ---")
    
    if "centros" not in dados or not dados["centros"]:
        print("ERRO: Nenhum Centro de Trabalho cadastrado no sistema.")
        return

    if "roteiros" not in dados or not dados["roteiros"]:
        print("ERRO: Nenhum roteiro de produção cadastrado para vincular itens aos centros.")
        return

    if "mrp_calculado" not in dados or not dados["mrp_calculado"]:
        print("ERRO: Execute o cálculo MRP (Opção 4) primeiro para gerar as necessidades de produção.")
        return

    # Inicializa a carga alocada por centro e por semana [centro][semana]
    carga_centros = {ct: [0.0] * HORIZONTE_SEMANAS for ct in dados["centros"]}

    # Calcula a carga com base nas ordens planejadas ou liberações do MRP para itens fabricados (PA, SA)
    for codigo, resultado in dados["mrp_calculado"].items():
        tipo_item = dados["itens"].get(codigo, {}).get("tipo")
        if tipo_item in ["PA", "SA"] and codigo in dados["roteiros"]:
            roteiro = dados["roteiros"][codigo]
            centro = roteiro["centro"]
            tempo_unitario = roteiro["tempo_unitario"] # horas por unidade

            liberacao = resultado["liberacao"]
            if centro in carga_centros:
                for semana in range(HORIZONTE_SEMANAS):
                    qtd_produzir = liberacao[semana]
                    if qtd_produzir > 0:
                        horas_necessarias = qtd_produzir * tempo_unitario
                        carga_centros[centro][semana] += horas_necessarias

    print("\n" + "=" * 90)
    print(" RELATÓRIO DE CARGA X CAPACIDADE DOS CENTROS DE TRABALHO ")
    print("=" * 90)

    for ct_cod, ct_info in sorted(dados["centros"].items()):
        capacidade_disponivel = ct_info["capacidade_semanal"]
        cargas_semana = carga_centros[ct_cod]

        print(f"\nCentro: {ct_cod} - {ct_info['descricao']} (Capacidade Semanal: {capacidade_disponivel:.1f} h)")
        print(f"  Semana        | " + " | ".join([f"S{i}" for i in range(1, HORIZONTE_SEMANAS + 1)]))
        print("  " + "-" * 70)
        print(f"  Carga (h)     | " + " | ".join([f"{x:<5.1f}" for x in cargas_semana]))
        
        # Análise de sobrecarga
        tem_sobrecarga = False
        for s, carga in enumerate(cargas_semana):
            if carga > capacidade_disponivel:
                tem_sobrecarga = True
                print(f"  -> ALERTA: Sobrecarga na Semana {s+1}! Carga ({carga:.1f}h) excede a capacidade ({capacidade_disponivel:.1f}h).")

        if not tem_sobrecarga:
            print("  -> Status: Capacidade OK em todas as semanas do horizonte.")

    print("\n" + "=" * 90)
    print("Análise de capacidade concluída com sucesso!")