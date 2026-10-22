"""Módulo de Estrutura de Produto (BOM) e árvore indentada."""
from persistencia import carregar_json, salvar_json
from utils import ler_float, pausar

def gerenciar_estrutura():
    """Menu para gerenciar a estrutura de produtos (BOM)."""
    while True:
        print("\n--- GESTÃO DA ESTRUTURA DE PRODUTO (BOM) ---")
        print("1. Cadastrar Componente em Pai")
        print("2. Exibir Estrutura (Explosão BOM Indentada)")
        print("0. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_componente_bom()
        elif opcao == "2":
            exibir_estrutura_bom()
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")

def cadastrar_componente_bom():
    """Cadastra a relação de um componente filho em um item pai respeitando as regras de nível."""
    itens = carregar_json("itens.json")
    estrutura = carregar_json("estrutura.json") # Dicionário ou lista de relações
    
    codigo_pai = input("Código do Item Pai (PA ou SA): ").strip()
    if codigo_pai not in itens:
        print(f"ERRO: Item pai {codigo_pai} não encontrado.")
        pausar()
        return
        
    tipo_pai = itens[codigo_pai]["tipo"]
    if tipo_pai == "MP":
        print("ERRO: Matérias-primas (MP) não possuem estrutura de componentes.")
        pausar()
        return

    codigo_filho = input("Código do Componente Filho (SA ou MP): ").strip()
    if codigo_filho not in itens:
        print(f"ERRO: Item filho {codigo_filho} não encontrado.")
        pausar()
        return

    tipo_filho = itens[codigo_filho]["tipo"]
    
    # Validação de regras de negócio de níveis (RN03)
    if tipo_pai == "SA" and tipo_filho == "SA":
        print("ERRO: Um item Semiacabado (SA) só pode ter Matérias-Primas (MP) como componentes.")
        pausar()
        return
    if tipo_pai == "PA" and tipo_filho == "PA":
        print("ERRO: Um Produto Acabado não pode ter outro PA diretamente como componente.")
        pausar()
        return

    quantidade = ler_float("Quantidade do componente por unidade do pai: ")
    
    # Estrutura armazenada como lista de dicionários: {"pai": ..., "filho": ..., "qtde": ...}
    if not isinstance(estrutura, list):
        estrutura = []
        
    # Evitar duplicidade exata pai-filho
    for rel in estrutura:
        if rel["pai"] == codigo_pai and rel["filho"] == codigo_filho:
            rel["qtde"] = quantidade
            salvar_json("estrutura.json", estrutura)
            print("Sucesso: Relação atualizada!")
            pausar()
            return

    estrutura.append({"pai": codigo_pai, "filho": codigo_filho, "qtde": quantidade})
    salvar_json("estrutura.json", estrutura)
    print("Sucesso: Componente adicionado à BOM!")
    pausar()

def exibir_estrutura_bom():
    """Exibe a árvore indentada da BOM de um produto acabado (RF03)."""
    itens = carregar_json("itens.json")
    estrutura = carregar_json("estrutura.json")
    
    codigo_pa = input("Digite o código do Produto Acabado (ex: PA-001): ").strip()
    if codigo_pa not in itens or itens[codigo_pa]["tipo"] != "PA":
        print("ERRO: Produto Acabado não encontrado ou inválido.")
        pausar()
        return

    print(f"\n{codigo_pa} - {itens[codigo_pa]['descricao']}")
    
    # Função recursiva para percorrer os níveis da BOM
    def desenhar_filhos(pai_atual, nivel):
        if not isinstance(estrutura, list):
            return
        for rel in estrutura:
            if rel["pai"] == pai_atual:
                filho_cod = rel["filho"]
                qtde = rel["qtde"]
                if filho_cod in itens:
                    filho_obj = itens[filho_cod]
                    # Indentação baseada no nível
                    espacos = "    " * nivel
                    print(f"{espacos}{filho_cod} {filho_obj['descricao']} ........ {qtde} {filho_obj['unidade']}")
                    # Se for SA, busca os filhos dele (Nível 2)
                    if filho_obj["tipo"] == "SA":
                        desenhar_filhos(filho_cod, nivel + 1)

    desenhar_filhos(codigo_pa, 1)
    print("\nNíveis: 0 = PA | 1 = SA, MP diretos | 2 = MP de SA")
    pausar()