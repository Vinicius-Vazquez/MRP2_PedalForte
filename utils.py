from __future__ import annotations


def normalizar_codigo(codigo: str) -> str:
    """Normaliza códigos de itens, centros, ordens ou roteiros em maiúsculas e sem espaços extras."""
    if not isinstance(codigo, str):
        raise ValueError("O código deve ser um texto.")
    limpo = codigo.strip().upper()
    if not limpo:
        raise ValueError("O código não pode estar vazio.")
    return limpo


def normalizar_texto(texto: str) -> str:
    """Remove espaços nas extremidades e colapsa espaços internos duplicados."""
    if not isinstance(texto, str):
        raise ValueError("O valor informado deve ser um texto.")
    return " ".join(texto.strip().split())


def validar_texto_obrigatorio(texto: str, campo: str = "descrição") -> str:
    """Valida que um campo textual não fique vazio após normalização."""
    normalizado = normalizar_texto(texto)
    if not normalizado:
        raise ValueError(f"O campo '{campo}' é obrigatório e não pode ficar vazio.")
    return normalizado


def validar_semana(semana: int, total_semanas: int = 8) -> int:
    """Valida o número da semana dentro do horizonte planejado (ex.: 1 a 8)."""
    if isinstance(semana, bool) or not isinstance(semana, int):
        raise ValueError("A semana deve ser um número inteiro.")
    if total_semanas < 1:
        raise ValueError("O horizonte de semanas deve ser pelo menos 1.")
    if semana < 1 or semana > total_semanas:
        raise ValueError(f"A semana deve estar entre 1 e {total_semanas} (recebido: {semana}).")
    return semana


def formatar_numero(valor: int | float, decimais: int = 2) -> str:
    """Formata um número no padrão brasileiro (ex.: 1.250,50)."""
    if decimais < 0:
        raise ValueError("A quantidade de casas decimais não pode ser negativa.")
    numero = 0.0 if abs(float(valor)) < 1e-9 else float(valor)
    texto = f"{numero:,.{decimais}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_moeda(valor: int | float, simbolo: str = "R$") -> str:
    """Formata um valor monetário no padrão brasileiro (ex.: R$ 1.250,50)."""
    return f"{simbolo} {formatar_numero(valor, decimais=2)}"


def formatar_percentual(valor: int | float, decimais: int = 1) -> str:
    """Formata um percentual (ex.: 85,0%)."""
    return f"{formatar_numero(valor, decimais=decimais)}%"


def ler_texto_obrigatorio(prompt: str, campo: str = "valor") -> str:
    """Lê do terminal um texto não vazio e normalizado."""
    while True:
        bruto = input(prompt)
        try:
            return validar_texto_obrigatorio(bruto, campo=campo)
        except ValueError as exc:
            print(f"Erro: {exc}")


def ler_codigo(prompt: str = "Código: ") -> str:
    """Lê do terminal um código normalizado (maiúsculas, sem espaços laterais)."""
    while True:
        bruto = input(prompt)
        try:
            return normalizar_codigo(bruto)
        except ValueError as exc:
            print(f"Erro: {exc}")


def ler_inteiro(
    prompt: str,
    minimo: int | None = None,
    maximo: int | None = None,
    permitir_vazio: bool = False,
    padrao: int | None = None,
) -> int | None:
    """Lê um número inteiro do terminal com validação opcional de faixa e valor padrão."""
    while True:
        bruto = input(prompt).strip()
        if not bruto:
            if permitir_vazio or padrao is not None:
                return padrao
            print("Erro: digite um número inteiro.")
            continue

        try:
            valor = int(bruto)
        except ValueError:
            print("Erro: entrada inválida. Digite apenas números inteiros.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Erro: o valor deve ser maior ou igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"Erro: o valor deve ser menor ou igual a {maximo}.")
            continue

        return valor


def ler_float(
    prompt: str,
    minimo: float | None = None,
    maximo: float | None = None,
    permitir_vazio: bool = False,
    padrao: float | None = None,
) -> float | None:
    """Lê um número decimal (aceitando vírgula ou ponto) com validação opcional."""
    while True:
        bruto = input(prompt).strip().replace(",", ".")
        if not bruto:
            if permitir_vazio or padrao is not None:
                return padrao
            print("Erro: digite um número válido.")
            continue

        try:
            valor = float(bruto)
        except ValueError:
            print("Erro: entrada inválida. Digite um número válido.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Erro: o valor deve ser maior ou igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"Erro: o valor deve ser menor ou igual a {maximo}.")
            continue

        return valor


def confirmar(prompt: str, padrao: bool = False) -> bool:
    """Solicita confirmação sim/não no terminal."""
    sufixo = " [S/n]: " if padrao else " [s/N]: "
    sim_opcoes = {"s", "sim", "y", "yes"}
    nao_opcoes = {"n", "nao", "não", "no"}

    while True:
        resposta = input(prompt + sufixo).strip().lower()
        if not resposta:
            return padrao
        if resposta in sim_opcoes:
            return True
        if resposta in nao_opcoes:
            return False
        print("Erro: responda com 's' (sim) ou 'n' (não).")


def iterar_componentes(estrutura_pai: object) -> list[tuple[str, float]]:
    """Normaliza os componentes de um item pai na BOM como pares (codigo_filho, quantidade)."""
    if isinstance(estrutura_pai, dict):
        return [(str(filho), float(qtd)) for filho, qtd in estrutura_pai.items()]
    if isinstance(estrutura_pai, list):
        pares: list[tuple[str, float]] = []
        for comp in estrutura_pai:
            if isinstance(comp, dict) and "componente" in comp and "quantidade" in comp:
                pares.append((str(comp["componente"]), float(comp["quantidade"])))
        return pares
    return []
