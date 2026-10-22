"""Módulo de Ordens de Produção (OP), Ordens de Compra (OC) e Apontamento."""
from persistencia import carregar_json, salvar_json
from utils import pausar
from mrp import executar_mrp_geral

def gerenciar_ordens():
    """Menu para gerir ordens e execução do MRP."""
    while True: # Loop principal do menu
        while True:
            print("\n--- GESTÃO DE ORDENS E MRP ---")
            print("1. Executar Cálculo MRP")
            print("2. Listar e Gerir Ordens (Firmar / Liberar / Apontar)")
            print("0. Voltar ao Menu Principal")
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == "1":
                executar_mrp_geral()
            elif opcao == "2":
                listar_e_gerir_ordens()
            elif opcao == "0":
                return
            else:
                print("Opção inválida!")

def listar_e_gerir_ordens():
    """Lista ordens geradas e permite alterar o seu estado (RF10, RF11)."""
    ordens = carregar_json("ordens.json")
    if not ordens:
        print("\nNenhuma ordem registada. Execute o MRP primeiro.")
        pausar()
        return

    print("\n--- ORDENS PLANEJADAS E GERADAS ---")
    print(f"{'ID':<8} | {'Tipo':<4} | {'Item':<8} | {'Qtde':<6} | {'Lib':<4} | {'Ent':<4} | {'Status'}")
    print("-" * 55)
    
    for idx, o in enumerate(ordens):
        print(f"[{idx}] {o['id']:<5} | {o['tipo']:<4} | {o['codigo_item']:<8} | {o['quantidade']:<6} | {o['semana_liberacao']:<4} | {o['semana_entrega']:<4} | {o['status']}")

    print("\nAções: [F]irmar ordem | [L]iberar ordem | [A]pontar produção | [V]oltar")
    acao = input("Escolha a ação: ").upper()
    
    if acao == "V":
        return
        
    idx_str = input("Digite o número do índice [ ] da ordem correspondente: ")
    try:
        idx = int(idx_str)
        if idx < 0 or idx >= len(ordens):
            print("Índice inválido.")
            pausar()
            return
    except ValueError:
        print("Digite um número válido.")
        pausar()
        return

    ordem_selecionada = ordens[idx]
    
    if acao == "F":
        ordem_selecionada["status"] = "FIRME"
        print(f"Sucesso: Ordem {ordem_selecionada['id']} marcada como FIRME.")
    elif acao == "L":
        ordem_selecionada["status"] = "LIBERADA"
        print(f"Sucesso: Ordem {ordem_selecionada['id']} marcada como LIBERADA.")
    elif acao == "A":
        if ordem_selecionada["status"] != "LIBERADA":
            print("ERRO: Apenas ordens com status LIBERADA podem ser apontadas.")
        else:
            ordem_selecionada["status"] = "ENCERRADA"
            print(f"Sucesso: Apontamento realizado! OP {ordem_selecionada['id']} encerrada com baixa de stock.")
    
    salvar_json("ordens.json", ordens)
    pausar()