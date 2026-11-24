"""Módulo de cadastro de centros de trabalho, roteiros e análise de Carga x Capacidade (CRP) (RF06, RF12)."""
from utils import ler_float, ler_texto_obrigatorio

HORIZONTE_SEMANAS = 8


def cadastrar_centro_trabalho(dados: dict) -> None:
    """Cadastra um novo Centro de Trabalho (RF06)."""
    print("\n--- CADASTRO DE CENTRO DE TRABALHO ---")
    codigo = ler_codigo("Código do centro (ex: CT-01): ")
    if codigo in dados["centros"]:
        print(f"ERRO: Centro '{codigo}' já cadastrado.")
        return

    descricao = ler_texto_obrigatorio(
        "Descrição do centro (ex: Usinagem e Solda): ",
        campo="descrição",
    )

    capacidade = ler_float("Capacidade semanal (horas/semana): ", minimo=0.1)
    custo_hora = ler_float("Custo por hora (R$): ", minimo=0.0)
    if capacidade is None or custo_hora is None:
        print("ERRO: Valores numéricos inválidos.")
        return

    dados["centros"][codigo] = {
        "codigo": codigo,
        "descricao": descricao,
        "capacidade_semanal": capacidade,
        "custo_hora": custo_hora,
    }
    print(f"Sucesso: Centro de Trabalho '{codigo}' cadastrado!")


def listar_centros_trabalho(dados: dict) -> None:
    """Lista os Centros de Trabalho cadastrados."""
    print("\n--- CENTROS DE TRABALHO CADASTRADOS ---")
    if not dados["centros"]:
        print("Nenhum centro cadastrado.")
        return
    print(f"{'Código':<10} | {'Descrição':<30} | {'Cap. Semanal (h)':<18} | {'Custo/h (R$)':<12}")
    print("-" * 78)
    for cod, ct in sorted(dados["centros"].items()):
        print(f"{cod:<10} | {ct['descricao']:<30} | {ct['capacidade_semanal']:<18.1f} | R$ {ct['custo_hora']:<9.2f}")


def gerenciar_centros(dados: dict) -> None:
    """Submenu para Centros de Trabalho."""
    while True:
        print("\n--- GESTÃO DE CENTROS DE TRABALHO ---")
        print("1. Cadastrar novo centro de trabalho")
        print("2. Listar centros cadastrados")
        print("0. Voltar")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            cadastrar_centro_trabalho(dados)
        elif op == "2":
            listar_centros_trabalho(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")


def cadastrar_roteiro(dados: dict) -> None:
    """Cadastra o roteiro de operação única para um item fabricado (PA ou SA) (RF06)."""
    print("\n--- CADASTRO DE ROTEIRO DE PRODUÇÃO ---")
    if not dados["centros"]:
        print("ERRO: Cadastre pelo menos um Centro de Trabalho primeiro.")
        return

    item_cod = input("Código do item fabricado (PA ou SA): ").strip().upper()
    if item_cod not in dados["itens"]:
        print(f"ERRO: Item '{item_cod}' não encontrado.")
        return
    if dados["itens"][item_cod]["tipo"] not in ["PA", "SA"]:
        print("ERRO: Roteiros só podem ser cadastrados para itens fabricados (PA ou SA).")
        return

    centro_cod = input("Código do Centro de Trabalho responsável: ").strip().upper()
    if centro_cod not in dados["centros"]:
        print(f"ERRO: Centro '{centro_cod}' não encontrado.")
        return

    tempo = ler_float("Tempo unitário de produção (em horas/unidade, ex: 0.5): ", minimo=0.0001)
    if tempo is None:
        print("ERRO: Tempo unitário deve ser maior que zero.")
        return
        return

    dados["roteiros"][item_cod] = {
        "item": item_cod,
        "centro": centro_cod,
        "tempo_unitario": tempo
    }
    print(f"Sucesso: Roteiro do item '{item_cod}' vinculado ao centro '{centro_cod}' ({tempo} h/un)!")


def listar_roteiros(dados: dict) -> None:
    """Lista os roteiros cadastrados."""
    print("\n--- ROTEIROS DE PRODUÇÃO CADASTRADOS ---")
    if not dados["roteiros"]:
        print("Nenhum roteiro cadastrado.")
        return
    print(f"{'Item':<10} | {'Centro':<10} | {'Tempo Unitário (h/un)':<22}")
    print("-" * 48)
    for item_cod, rot in sorted(dados["roteiros"].items()):
        print(f"{item_cod:<10} | {rot['centro']:<10} | {rot['tempo_unitario']:<22.2f}")


def gerenciar_roteiros(dados: dict) -> None:
    """Submenu para Roteiros de Produção."""
    while True:
        print("\n--- GESTÃO DE ROTEIROS DE PRODUÇÃO ---")
        print("1. Cadastrar/Alterar roteiro de item")
        print("2. Listar roteiros cadastrados")
        print("0. Voltar")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            cadastrar_roteiro(dados)
        elif op == "2":
            listar_roteiros(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")


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

    carga_centros = {ct: [0.0] * HORIZONTE_SEMANAS for ct in dados["centros"]}

    for codigo, resultado in dados["mrp_calculado"].items():
        tipo_item = dados["itens"].get(codigo, {}).get("tipo")
        if tipo_item in ["PA", "SA"] and codigo in dados["roteiros"]:
            roteiro = dados["roteiros"][codigo]
            centro = roteiro["centro"]
            tempo_unitario = roteiro["tempo_unitario"]

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
        
        tem_sobrecarga = False
        for s, carga in enumerate(cargas_semana):
            if carga > capacidade_disponivel:
                tem_sobrecarga = True
                print(f"  -> ALERTA: Sobrecarga na Semana {s+1}! Carga ({carga:.1f}h) excede a capacidade ({capacidade_disponivel:.1f}h).")

        if not tem_sobrecarga:
            print("  -> Status: Capacidade OK em todas as semanas do horizonte.")

    print("\n" + "=" * 90)
    print("Análise de capacidade concluída com sucesso!")
