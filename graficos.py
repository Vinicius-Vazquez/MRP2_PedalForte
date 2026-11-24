"""Módulo de visualização gráfica de dados e indicadores usando Matplotlib (RF16)."""

from pathlib import Path
import matplotlib.pyplot as plt


def _salvar_e_exibir(nome_arquivo: str) -> None:
    """Salva o gráfico atual em PNG na pasta data/ e exibe na tela (RF16)."""
    pasta_data = Path("data")
    pasta_data.mkdir(parents=True, exist_ok=True)
    caminho_png = pasta_data / nome_arquivo
    plt.savefig(caminho_png, dpi=150)
    print(f"Gráfico salvo em '{caminho_png}'.")
    print("Exibindo janela do gráfico... (Feche a janela do gráfico para retornar ao sistema)")
    plt.show()
    plt.close()


def _iterar_ordens(dados: dict) -> list[dict]:
    """Retorna lista de dicionários de ordens independentemente de dict ou list."""
    ordens = dados.get("ordens", {})
    if isinstance(ordens, dict):
        return [o for o in ordens.values() if isinstance(o, dict)]
    if isinstance(ordens, list):
        return [o for o in ordens if isinstance(o, dict)]
    return []


def gerar_grafico_estoque(dados: dict) -> None:
    """1. Gráfico de barras: saldo atual x estoque de segurança de cada item (RF16)."""
    print("\n--- GERANDO GRÁFICO DE ESTOQUE ---")

    itens = dados.get("itens", {})
    if not itens:
        print("ERRO: Nenhum item cadastrado.")
        return

    codigos = []
    saldos = []
    seguranca = []

    for codigo, item in sorted(itens.items()):
        codigos.append(codigo)
        saldos.append(float(dados.get("estoque", {}).get(codigo, {}).get("saldo_atual", 0.0)))
        seguranca.append(float(item.get("estoque_seguranca", 0.0)))

    plt.figure(figsize=(10, 6))
    x = list(range(len(codigos)))
    largura = 0.35

    plt.bar([i - largura / 2 for i in x], saldos, largura, label="Saldo Atual", color="steelblue")
    plt.bar([i + largura / 2 for i in x], seguranca, largura, label="Estoque de Segurança", color="indianred")

    plt.xlabel("Códigos dos Itens")
    plt.ylabel("Quantidade")
    plt.title("Comparativo: Saldo Atual x Estoque de Segurança")
    plt.xticks(x, codigos, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()

    _salvar_e_exibir("grafico_estoque_seguranca.png")


def gerar_grafico_estoque_projetado(dados: dict) -> None:
    """2. Gráfico de estoque projetado de um item nas 8 semanas do MRP com linha do ES (RF16)."""
    print("\n--- GERANDO GRÁFICO DE ESTOQUE PROJETADO (8 SEMANAS) ---")

    itens = dados.get("itens", {})
    mrp_calc = dados.get("mrp_calculado")
    if not itens:
        print("ERRO: Nenhum item cadastrado.")
        return
    if not isinstance(mrp_calc, dict) or not mrp_calc:
        print("ERRO: Execute o cálculo MRP (Opção 4) antes de gerar este gráfico.")
        return

    cod_item = input("Código do item (ex.: PA-001 ou SA-020): ").strip().upper()
    if cod_item not in itens or cod_item not in mrp_calc:
        print(f"ERRO: Item '{cod_item}' não encontrado ou sem resultado no MRP.")
        return

    est_proj = mrp_calc[cod_item].get("estoque_projetado", [0.0] * 8)
    es = float(itens[cod_item].get("estoque_seguranca", 0.0))
    semanas = list(range(1, len(est_proj) + 1))

    plt.figure(figsize=(10, 6))
    plt.plot(semanas, est_proj, marker="o", linewidth=2, color="steelblue", label="Estoque Projetado")
    plt.axhline(es, color="crimson", linestyle="--", linewidth=2, label=f"Estoque de Segurança ({es:.1f})")

    plt.xlabel("Semana")
    plt.ylabel("Quantidade")
    plt.title(f"Estoque Projetado nas 8 Semanas - {cod_item} ({itens[cod_item].get('descricao', '')})")
    plt.xticks(semanas, [f"S{s}" for s in semanas])
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    _salvar_e_exibir(f"grafico_estoque_projetado_{cod_item.lower()}.png")


def gerar_grafico_ordens_semana_entrega(dados: dict) -> None:
    """3. Gráfico de barras empilhadas: OP e OC por semana de entrega (RF16)."""
    print("\n--- GERANDO GRÁFICO DE ORDENS POR SEMANA DE ENTREGA ---")

    ordens = _iterar_ordens(dados)
    if not ordens:
        print("ERRO: Nenhuma ordem cadastrada ou gerada.")
        return

    itens = dados.get("itens", {})
    semanas = list(range(1, 9))
    qtd_op = [0.0] * 8
    qtd_oc = [0.0] * 8

    for ordem in ordens:
        tipo = str(ordem.get("tipo", "")).upper()
        qtd = float(ordem.get("quantidade", 0.0))
        if qtd <= 0:
            continue

        sem_entrega = ordem.get("semana_entrega")
        if sem_entrega is None:
            cod_item = str(ordem.get("item", ""))
            lt = int(itens.get(cod_item, {}).get("lead_time", 0))
            sem_entrega = int(ordem.get("semana", 0)) + lt

        sem_int = int(sem_entrega)
        if 1 <= sem_int <= 8:
            if tipo == "OP":
                qtd_op[sem_int - 1] += qtd
            elif tipo == "OC":
                qtd_oc[sem_int - 1] += qtd

    plt.figure(figsize=(10, 6))
    plt.bar(semanas, qtd_op, label="Ordens de Produção (OP)", color="steelblue")
    plt.bar(semanas, qtd_oc, bottom=qtd_op, label="Ordens de Compra (OC)", color="darkorange")

    plt.xlabel("Semana de Entrega")
    plt.ylabel("Quantidade")
    plt.title("Ordens de Produção (OP) e Compra (OC) por Semana de Entrega")
    plt.xticks(semanas, [f"S{s}" for s in semanas])
    plt.legend()
    plt.tight_layout()

    _salvar_e_exibir("grafico_ordens_entrega.png")


def gerar_grafico_crp(dados: dict) -> None:
    """4. Gráfico de carga x capacidade por semana de um centro de trabalho (RF16)."""
    print("\n--- GERANDO GRÁFICO DE CARGA X CAPACIDADE (CRP) ---")
    centros = dados.get("centros", {})
    if not centros:
        print("ERRO: Nenhum centro de trabalho cadastrado.")
        return

    cod_ct = input("Código do centro de trabalho (ex.: CT-01): ").strip().upper()
    if cod_ct not in centros:
        print(f"ERRO: Centro de trabalho '{cod_ct}' não encontrado.")
        return

    cap_semanal = float(centros[cod_ct].get("capacidade_semanal", 0.0))
    semanas = list(range(1, 9))
    carga = [0.0] * 8
    roteiros = dados.get("roteiros", {})

    for ordem in _iterar_ordens(dados):
        if str(ordem.get("tipo", "")).upper() == "OP" and str(ordem.get("status", "")).upper() == "LIBERADA":
            item_cod = str(ordem.get("item", ""))
            roteiro = roteiros.get(item_cod)
            if isinstance(roteiro, dict) and str(roteiro.get("centro", "")).upper() == cod_ct:
                sem = int(ordem.get("semana", 0))
                if 1 <= sem <= 8:
                    carga[sem - 1] += float(ordem.get("quantidade", 0.0)) * float(roteiro.get("tempo_unitario", 0.0))

    cores = ["crimson" if c > cap_semanal else "steelblue" for c in carga]

    plt.figure(figsize=(10, 6))
    plt.bar(semanas, carga, color=cores, label="Carga Planejada (h)")
    plt.axhline(cap_semanal, color="darkgreen", linestyle="--", linewidth=2, label=f"Capacidade ({cap_semanal:.1f} h)")

    plt.xlabel("Semana")
    plt.ylabel("Horas")
    plt.title(f"Carga x Capacidade - {cod_ct} ({centros[cod_ct].get('descricao', '')})")
    plt.xticks(semanas, [f"S{s}" for s in semanas])
    plt.legend()
    plt.tight_layout()

    _salvar_e_exibir(f"grafico_crp_{cod_ct.lower()}.png")


def gerenciar_graficos(dados: dict) -> None:
    """Submenu para visualização de gráficos gerenciais (RF16)."""
    while True:
        print("\n--- GRÁFICOS DE GESTÃO ---")
        print("1. Saldo atual x Estoque de segurança (por item)")
        print("2. Estoque projetado nas 8 semanas do MRP (por item)")
        print("3. Ordens (OP e OC) por semana de entrega (barras empilhadas)")
        print("4. Carga x Capacidade (CRP) por centro de trabalho")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            gerar_grafico_estoque(dados)
        elif op == "2":
            gerar_grafico_estoque_projetado(dados)
        elif op == "3":
            gerar_grafico_ordens_semana_entrega(dados)
        elif op == "4":
            gerar_grafico_crp(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")
            