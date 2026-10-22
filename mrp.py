"""Módulo de cálculo do MRP (Manufacturing Requirements Planning)."""
from persistencia import carregar_json, salvar_json
from estoque import calcular_saldo_atual
from utils import pausar

def executar_mrp_geral():
    """Executa o cálculo MRP para todos os itens seguindo a sequência RN04 (PA -> SA -> MP)."""
    itens = carregar_json("itens.json") or {}
    estrutura = carregar_json("estrutura.json") or {}
    mps = carregar_json("mps.json") or {}
    ordens_atuais = carregar_json("ordens.json") or []
    
    if not isinstance(ordens_atuais, list):
        ordens_atuais = []

    # RN08: Ordens PLANEJADAS são apagadas e recalculadas a cada execução do MRP.
    ordens_filtradas = [o for o in ordens_atuais if o.get("status") in ["FIRME", "LIBERADA", "ENCERRADA"]]

    pas = [k for k, v in itens.items() if v.get("tipo") == "PA"]
    sas = [k for k, v in itens.items() if v.get("tipo") == "SA"]
    mps_itens = [k for k, v in itens.items() if v.get("tipo") == "MP"]

    novas_ordens = list(ordens_filtradas)

    # 1. Processar Produtos Acabados (PA) com base no MPS
    for pa in pas:
        demanda_pa = mps.get(pa, {})
        if not isinstance(demanda_pa, dict):
            demanda_pa = {}
            
        item_obj = itens[pa]
        lt = item_obj.get("lead_time", 1)
        es = item_obj.get("estoque_seguranca", 0)
        lote_min = item_obj.get("lote_minimo", 1)
        estoque_inicial = calcular_saldo_atual(pa)
        
        ep_anterior = estoque_inicial
        for i in range(1, 9):
            sem_str = f"S{i}"
            nb = int(demanda_pa.get(sem_str, 0) or 0)
            
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
                    sem_lib_str = "S1"
                    status_ordem = "ATRASADA (Necessário antes de S1)"
                else:
                    sem_lib_str = f"S{sem_liberacao}"
                    status_ordem = "PLANEJADA"
                
                # Registar nova ordem planejada de forma segura
                novas_ordens.append({
                    "ordem": f"OP-{pa}-{sem_lib_str}",
                    "codigo_item": pa,
                    "quantidade": rp_plan,
                    "semana_entrega": sem_str,
                    "semana_liberacao": sem_lib_str,
                    "status": status_ordem
                })

    # Guardar ordens atualizadas
    salvar_json("ordens.json", novas_ordens)
    print("Cálculo MRP executado com sucesso!")