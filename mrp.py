"""Módulo de cálculo do MRP (Manufacturing Requirements Planning)."""
from persistencia import carregar_json, salvar_json
from estoque import calcular_saldo_atual
from utils import pausar

def executar_mrp_geral():
    """Executa o cálculo MRP para todos os itens seguindo a sequência RN04 (PA -> SA -> MP)."""
    itens = carregar_json("itens.json")
    estrutura = carregar_json("estrutura.json")
    mps = carregar_json("mps.json")
    ordens_atuais = carregar_json("ordens.json")
    
    if not isinstance(ordens_atuais, list):
        ordens_atuais = []

    # RN08: Ordens PLANEJADAS são apagadas e recalculadas a cada execução do MRP.
    ordens_filtradas = [o for o in ordens_atuais if o.get("status") in ["FIRME", "LIBERADA", "ENCERRADA"]]

    # Organizar itens por tipo: PA, depois SA, depois MP (RN04)
    pas = [k for k, v in itens.items() if v["tipo"] == "PA"]
    sas = [k for k, v in itens.items() if v["tipo"] == "SA"]
    mps_itens = [k for k, v in itens.items() if v["tipo"] == "MP"]

    # Dicionário para armazenar as liberações planejadas de cada item por semana: {codigo: {S1: qtd, S2: qtd, ...}}
    liberacoes_planejadas_global = {codigo: {f"S{i}": 0 for i in range(1, 9)} for codigo in itens}
    
    # 1. Processar Produtos Acabados (PA) com base no MPS
    for pa in pas:
        demanda_pa = mps.get(pa, {})
        item_obj = itens[pa]
        lt = item_obj["lead_time"]
        es = item_obj["estoque_seguranca"]
        lote_min = item_obj["lote_minimo"]
        estoque_inicial = calcular_saldo_atual(pa)
        
        ep_anterior = estoque_inicial
        for i in range(1, 9):
            sem_str = f"S{i}"
            nb = demanda_pa.get(sem_str, 0)
            
            # RP: apenas ordens FIRMES ou LIBERADAS (RN08)
            rp = sum(o["quantidade"] for o in ordens_filtradas if o["codigo_item"] == pa and o.get("semana_entrega") == sem_str and o["status"] in ["FIRME", "LIBERADA"])
            
            # RN05: Necessidade líquida NL(t) = max(0, NB(t) + ES - (EP(t-1) + RP(t)))
            nl = max(0, nb + es - (ep_anterior + rp))
            
            # RN06: Recebimento planejado (RP_plan) = maior valor entre NL e lote mínimo (se NL > 0)
            rp_plan = max(nl, lote_min) if nl > 0 else 0
            
            # Estoque projetado EP(t) = EP(t-1) + RP(t) + RP_plan(t) - NB(t)
            ep = ep_anterior + rp + rp_plan - nb
            ep_anterior = ep
            
            # RN07: Liberação planejada ocorre na semana do recebimento menos o lead time
            if rp_plan > 0:
                sem_liberacao = i - lt
                if sem_liberacao < 1:
                    sem_lib_str = "S0" # Indicador de atraso
                    status_ordem = "ATRASADA"
                else:
                    sem_lib_str = f"S{sem_liberacao}"
                    status_ordem = "PLANEJADA"
                
                liberacoes_