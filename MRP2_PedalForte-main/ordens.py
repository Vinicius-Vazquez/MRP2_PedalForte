"""Módulo de geração, consulta e gestão de Ordens de Produção (OP) e Ordens de Compra (OC) (RF10, RF11)."""

def gerar_ordens_automaticas(dados: dict) -> None:
    """Gera ordens de produção e de compra com base nas liberações planejadas do cálculo MRP (RF10, RF11)."""
    print("\n--- GERAÇÃO DE ORDENS (MRP -> OP / OC) ---")
    
    if "mrp_calculado" not in dados or not dados["mrp_calculado"]:
        print("ERRO: Execute o cálculo MRP (Opção 4) antes de gerar as ordens.")
        return

    # Garante estrutura de ordens no dicionário
    if "ordens" not in dados or not isinstance(dados["ordens"], dict):
        dados["ordens"] = {}

    contador_op = len([o for o in dados["ordens"].values() if o["tipo"] == "OP"]) + 1
    contador_oc = len([o for o in dados["ordens"].values() if o["tipo"] == "OC"]) + 1

    novas_geradas = 0

    for codigo, resultado in dados["mrp_calculado"].items():
        liberacao = resultado["liberacao"]
        tipo_item = dados["itens"][codigo]["tipo"] # PA, SA ou MP

        for semana, qtd in enumerate(liberacao):
            if qtd > 0:
                # Verifica se já existe uma ordem parecida gerada para este item nesta semana para evitar duplicação em execuções repetidas
                duplicada = False
                for ord_existente in dados["ordens"].values():
                    if (ord_existente["item"] == codigo and 
                        ord_existente["semana"] == semana + 1 and 
                        ord_existente["quantidade"] == qtd and
                        ord_existente["status"] == "PLANEJADA"):
                        duplicada = True
                        break

                if not duplicada:
                    if tipo_item in ["PA", "SA"]:
                        num_ordem = f"OP-{contador_op:03d}"
                        contador_op += 1
                        tipo_ordem = "OP"
                    else:
                        num_ordem = f"OC-{contador_oc:03d}"
                        contador_oc += 1
                        tipo_ordem = "OC"

                    dados["ordens"][num_ordem] = {
                        "codigo_ordem": num_ordem,
                        "tipo": tipo_ordem,
                        "item": codigo,
                        "quantidade": qtd,
                        "semana": semana + 1,
                        "status": "PLANEJADA"
                    }
                    novas_geradas += 1

    print(f"Sucesso: {novas_geradas} novas ordens (OPs e OCs) geradas com base no MRP!")

def listar_ordens(dados: dict) -> None:
    """Lista todas as Ordens de Produção e de Compra cadastradas no sistema (RF10, RF11)."""
    print("\n--- LISTA DE ORDENS DE PRODUÇÃO E COMPRA ---")
    
    ordens = dados.get("ordens", {})
    if not ordens:
        print("Nenhuma ordem cadastrada ou gerada até o momento.")
        return

    print(f"{'Ordem':<10} | {'Tipo':<5} | {'Item':<10} | {'Quantidade':<12} | {'Semana':<8} | {'Status':<12}")
    print("-" * 70)
    for num_ordem, ord_info in sorted(ordens.items()):
        print(f"{num_ordem:<10} | {ord_info['tipo']:<5} | {ord_info['item']:<10} | {ord_info['quantidade']:<12.1f} | {ord_info['semana']:<8} | {ord_info['status']:<12}")

def gerenciar_ordens(dados: dict) -> None:
    """Submenu para gestão de ordens."""
    while True:
        print("\n--- GESTÃO DE ORDENS DE PRODUÇÃO E COMPRA ---")
        print("1. Gerar ordens automaticamente a partir do MRP")
        print("2. Listar todas as ordens (OP / OC)")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            gererar_ordens_automaticas(dados)
        elif op == "2":
            listar_ordens(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")