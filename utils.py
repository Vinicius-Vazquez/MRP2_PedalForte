"""Módulo de utilidades: validações de entrada e formatação."""

def ler_inteiro(mensagem: str) -> int:
    """Lê um número inteiro válido do usuário, tratando erros de entrada."""
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("ERRO: Digite um número inteiro válido.")

def ler_float(mensagem: str) -> float:
    """Lê um número decimal válido do usuário, tratando erros de entrada."""
    while True:
        try:
            # Substitui vírgula por ponto para evitar problemas com formato brasileiro
            entrada = input(mensagem).replace(',', '.')
            return float(entrada)
        except ValueError:
            print("ERRO: Digite um número decimal válido.")

def pausar():
    """Pausa a execução aguardando o usuário pressionar Enter."""
    input("\nPressione <Enter> para continuar...")