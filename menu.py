"""Módulo de interface em modo texto para navegação nos menus do sistema."""
from itens import gerenciar_itens
from estrutura import gerenciar_estrutura

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
            gerenciar_itens(dados)
        elif opcao == "2":
            gerenciar_estrutura(dados)
        elif opcao == "3":
            print("[Esqueleto] MPS")
        elif opcao == "4":
            print("[Esqueleto] MRP")
        elif opcao == "5":
            print("[Esqueleto] Ordens")
        elif opcao == "6":
            print("[Esqueleto] CRP")
        elif opcao == "7":
            print("[Esqueleto] Custo Padrão")
        elif opcao == "8":
            print("[Esqueleto] Relatórios")
        elif opcao == "9":
            print("[Esqueleto] Gráficos")
        elif opcao == "0":
            break
        else:
            print("ERRO: Opcao invalida. Tente novamente.")