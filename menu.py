"""Módulo de menus e navegação principal (RF01)."""
from itens import gerenciar_itens
from estrutura import gerenciar_estrutura
from estoque import gerenciar_estoque
from mps import gerenciar_mps
from ordens import gerenciar_ordens, executar_mrp_geral
from capacidade import gerenciar_capacidade
from custos import calcular_custo_padrao
from relatorios import exportar_relatorios_csv
from graficos import gerar_graficos
from persistencia import inicializar_base_demonstracao

def executar_menu_principal():
    """Exibe o menu principal do sistema MRP II (RF01)."""
    inicializar_base_demonstracao()
    
    while True:
        print("\n=============================================")
        print("       MRP II - PEDAL FORTE BICICLETAS       ")
        print("=============================================")
        print("1. Cadastros (Itens, Estrutura BOM, Centros, Roteiros)")
        print("2. Estoque (Movimentar, Saldo, Kardex)")
        print("3. Plano Mestre de Produção (MPS)")
        print("4. Executar MRP")
        print("5. Ordens de Produção e de Compra")
        print("6. Carga x Capacidade (CRP)")
        print("7. Custo Padrão dos Produtos")
        print("8. Relatórios (Exportar CSV)")
        print("9. Gráficos de Gestão (Matplotlib)")
        print("0. Sair")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\nSubmenu de Cadastros:")
            print("1. Gerenciar Itens")
            print("2. Gerenciar Estrutura (BOM)")
            print("3. Gerenciar Centros de Trabalho e Roteiros")
            sub = input("Escolha: ")
            if sub == "1":
                gerenciar_itens()
            elif sub == "2":
                gerenciar_estrutura()
            elif sub == "3":
                gerenciar_capacidade()
        elif opcao == "2":
            gerenciar_estoque()
        elif opcao == "3":
            gerenciar_mps()
        elif opcao == "4":
            executar_mrp_geral()
        elif opcao == "5":
            gerenciar_ordens()
        elif opcao == "6":
            gerenciar_capacidade()
        elif opcao == "7":
            calcular_custo_padrao()
        elif opcao == "8":
            exportar_relatorios_csv()
        elif opcao == "9":
            gerar_graficos()
        elif opcao == "0":
            print("\nEncerrando o sistema MRP II. Até logo!")
            break
        else:
            print("Opção inválida! Escolha uma opção entre 0 e 9.")