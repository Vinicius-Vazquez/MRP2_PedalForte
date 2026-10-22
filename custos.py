"""Módulo de cálculo de custo padrão (RF13)."""
from persistencia import carregar_json
from utils import pausar

def calcular_custo_padrao():
    """Calcula o custo padrão de um produto acabado percorrendo a BOM e custos unitários (RF13)."""
    itens = carregar_json("itens.json")
    estrutura = carregar_json("estrutura.json")
    roteiros = carregar_json("roteiros.json")
    centros = carregar_json("centros.json")
    
    codigo_pa = input("Digite o código do Produto Acabado (ex: PA-001): ").strip()
    if codigo_pa not in itens or itens[codigo_pa]["tipo"] != "PA":
        print("ERRO: Produto Acabado não encontrado.")
        pausar()
        return

    print(f"\nCUSTO PADRÃO - {codigo_pa} {itens[codigo_pa]['descricao']}")
    print(f"{'Item':<8} | {'Descrição':<25} | {'Qtde':<5} | {'Custo un.':<10} | {'Total'}")
    print("-" * 65)

    def somar_componentes(pai_cod):
        nao_local_custo = 0.0
        if not isinstance(estrutura, list):
            return 0.0
        for rel in estrutura:
            if rel["pai"] == pai_cod:
                filho_cod = rel["filho"]
                qtde = rel["qtde"]
                if filho_cod in itens:
                    filho_obj = itens[filho_cod]
                    if filho_obj["tipo"] == "MP":
                        c_unit = filho_obj["custo_unitario"]
                        subtotal = qtde * c_unit
                        print(f"{filho_cod:<8} | {filho_obj['descricao']:<25} | {qtde:<5} | R$ {c_unit:<7.2f} | R$ {subtotal:.2f}")
                        nao_local_custo += subtotal
                    elif filho_obj["tipo"] == "SA":
                        print(f"{filho_cod:<8} | {filho_obj['descricao']:<25} | {qtde:<5} | (Semiacabado)")
                        nao_local_custo += qtde * somar_componentes(filho_cod)
        return nao_local_custo

    custo_materiais = somar_componentes(codigo_pa)
    
    custo_mo = 0.0
    if codigo_pa in roteiros:
        rot = roteiros[codigo_pa]
        ct_id = rot["codigo_ct"]
        tempo = rot["tempo_unitario"]
        if ct_id in centros:
            custo_hora = centros[ct_id]["custo_hora"]
            custo_mo = tempo * custo_hora
            print(f"Mão de obra {ct_id} | {tempo} h x R$ {custo_hora:.2f} | R$ {custo_mo:.2f}")

    custo_total = custo_materiais + custo_mo
    print("-" * 65)
    print(f"CUSTO PADRÃO TOTAL: R$ {custo_total:.2f}")
    pausar()