"""Módulo de interface em modo texto para navegação nos menus do sistema."""

from itens import gerenciar_itens
from estrutura import gerenciar_estrutura
from estoque import gerenciar_estoque

def sub_menu_cadastros(dados: dict) -> None:
    """Submenu para gerenciamento de cadastros (Itens e Estrutura BOM)."""
    while True:
        print("\n--- MENU DE CADASTROS ---")
        print("1. Gerenciar Itens (PA, SA, MP)")
        print("2. Gerenciar Estrutura de Produto (BOM)")
        print("0. Voltar ao menu principal")
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            gerenciar_itens(dados)
        elif op == "2":
            gerenciar_estrutura(dados)
        elif op == "0":
            break
        else:
            print("ERRO: Opção inválida.")

def exibir_menu_principal(dados: dict) -> None:
    """Exibe o menu principal e direciona para as funcionalidades do sistema."""
    while True:
        print("\n" + "=" * 50)
        print(" MRP II - PEDAL FORTE BICICLETAS ")
        print("=" * 50)
        print("1. Cadastros (itens, estrutura, centros, roteiros)")
        print("2. Estoque (movimentar, saldo, kardex)")
        print("3. Plano Mestre de Producao (MPS)")
        print("4. Executar MRP")
        print("5. Ordens de producao e de compra")
        print("6. Carga x capacidade (CRP)")
        print("7. Custo padrao dos produtos")
        print("8. Relatorios (exportar CSV)")
        print("9. Graficos de Gestao (Matplotlib)")
        print("0. Sair")
        print("-" * 50)
        
        opcao = input("Escolha uma opcao: ").strip()
        
        if opcao == "1":
            sub_menu_cadastros(dados)
        elif opcao == "2":
            gerenciar_estoque(dados)
        elif opcao == "3":
            print("[Em desenvolvimento] MPS")
        elif opcao == "4":
            print("[Em desenvolvimento] MRP")
        elif opcao == "5":
            print("[Em desenvolvimento] Ordens")
        elif opcao == "6":
            print("[Em desenvolvimento] CRP")
        elif opcao == "7":
            print("[Em desenvolvimento] Custo Padrão")
        elif opcao == "8":
            print("[Em desenvolvimento] Relatórios")
        elif opcao == "9":
            print("[Em desenvolvimento] Gráficos")
        elif opcao == "0":
            break
        else:
            print("ERRO: Opcao invalida. Tente novamente.")