"""Módulo principal (ponto de entrada) do Sistema MRP II - Pedal Forte Bicicletas."""

from persistencia import carregar_dados, salvar_dados
from menu import exibir_menu_principal


def main() -> None:
    """Função principal que inicializa o sistema, carrega os dados e gerencia o fluxo."""
    print("Inicializando o sistema MRP II - Pedal Forte Bicicletas...")
    dados = carregar_dados()
        
    try:
        exibir_menu_principal(dados)
    finally:
        salvar_dados(dados)
        print("Dados salvos com sucesso. Encerrando o sistema.")

if __name__ == "__main__":
    main()
