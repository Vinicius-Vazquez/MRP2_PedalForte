"""Aplicação Web MRP II - Pedal Forte Bicicletas (Streamlit Integrado)"""
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

import persistencia
from persistencia import carregar_json, salvar_json, inicializar_base_demonstracao
from estoque import calcular_saldo_atual
import mrp

# INICIALIZAR BASE DE DEMONSTRAÇÃO
inicializar_base_demonstracao()

# Configuração da página
st.set_page_config(
    page_title="MRP II - Pedal Forte Bicicletas",
    page_icon="🚲",
    layout="wide"
)

# GARANTIR COMPATIBILIDADE DO CSV DE MOVIMENTOS
caminho_csv = os.path.join("data", "movimentos.csv")
os.makedirs("data", exist_ok=True)
if os.path.exists(caminho_csv) and os.path.getsize(caminho_csv) > 0:
    with open(caminho_csv, "r", encoding="utf-8") as f:
        primeira_linha = f.readline().strip()
    if "codigo_item" not in primeira_linha:
        with open(caminho_csv, "r", encoding="utf-8") as f:
            conteudo = f.read()
        with open(caminho_csv, "w", encoding="utf-8") as f:
            f.write("codigo_item,tipo,quantidade,observacao\n" + conteudo)
else:
    with open(caminho_csv, "w", encoding="utf-8") as f:
        f.write("codigo_item,tipo,quantidade,observacao\n")

st.title("🚲 MRP II - Pedal Forte Bicicletas")
st.markdown("Sistema integrado de Planeamento dos Recursos de Manufatura — Gestão Interativa")

# Menu Lateral
st.sidebar.header("Navegação do Sistema")
menu_opcao = st.sidebar.selectbox(
    "Escolha o Módulo",
    [
        "Visão Geral (Dashboard)",
        "Cadastrar / Gerir Itens",
        "Estrutura de Produtos (BOM)",
        "Roteiros de Produção",
        "Movimentar Estoque (Kardex)",
        "Plano Mestre (MPS)",
        "Executar MRP",
        "Gráficos de Gestão"
    ]
)

# --- 1. VISÃO GERAL ---
if menu_opcao == "Visão Geral (Dashboard)":
    st.header("Painel de Controlo da Fábrica")
    
    itens = carregar_json("itens.json")
    ordens = carregar_json("ordens.json")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Itens Cadastrados", len(itens) if itens else 0)
    col2.metric("Ordens Registadas", len(ordens) if isinstance(ordens, list) else 0)
    col3.metric("Horizonte MPS", "8 Semanas")
    
    st.markdown("---")
    st.subheader("Lista Completa de Itens e Saldos Atuais")
    if itens:
        dados_tabela = []
        for cod, item in itens.items():
            saldo = calcular_saldo_atual(cod)
            dados_tabela.append({
                "Código": cod,
                "Descrição": item["descricao"],
                "Tipo": item["tipo"],
                "Unidade": item["unidade"],
                "Saldo Atual": saldo,
                "Est. Segurança": item["estoque_seguranca"]
            })
        df_itens = pd.DataFrame(dados_tabela)
        st.dataframe(df_itens, use_container_width=True)
    else:
        st.info("Nenhum item encontrado.")

# --- 2. CADASTRAR / GERIR ITENS ---
elif menu_opcao == "Cadastrar / Gerir Itens":
    st.header("Gestão de Itens (Cadastrar / Remover)")
    
    tab_cad, tab_rem = st.tabs(["Cadastrar Novo Item", "Remover Item Existente"])
    
    with tab_cad:
        with st.form("form_item"):
            col1, col2 = st.columns(2)
            with col1:
                novo_cod = st.text_input("Código do Item (ex: PA-003 ou MP-400)")
                nova_desc = st.text_input("Descrição do Item")
                novo_tipo = st.selectbox("Tipo de Item", ["PA (Produto Acabado)", "SA (Subconjunto)", "MP (Matéria-Prima)"])
            with col2:
                nova_un = st.text_input("Unidade de Medida (ex: un, m, L, kg)", value="un")
                novo_est_seg = st.number_input("Estoque de Segurança", min_value=0, value=5)
                novo_lead = st.number_input("Lead Time (Semanas)", min_value=1, value=1)
                
            submitted = st.form_submit_button("Guardar Novo Item")
            if submitted:
                if novo_cod and nova_desc:
                    itens = carregar_json("itens.json") or {}
                    if novo_cod in itens:
                        st.error(f"O item com o código '{novo_cod}' já existe!")
                    else:
                        tipo_limpo = novo_tipo.split(" ")[0]
                        itens[novo_cod] = {
                            "descricao": nova_desc,
                            "tipo": tipo_limpo,
                            "unidade": nova_un,
                            "estoque_seguranca": int(novo_est_seg),
                            "lead_time": int(novo_lead)
                        }
                        salvar_json("itens.json", itens)
                        st.success(f"Item {novo_cod} registado com sucesso!")
                        st.rerun()
                else:
                    st.warning("Preencha pelo menos o Código e a Descrição.")
                    
    with tab_rem:
        itens_atuais = carregar_json("itens.json") or {}
        if itens_atuais:
            item_a_remover = st.selectbox("Selecione o Item para Remover", list(itens_atuais.keys()), format_func=lambda x: f"{x} - {itens_atuais[x]['descricao']}")
            if st.button("Apagar Item Selecionado"):
                if item_a_remover in itens_atuais:
                    del itens_atuais[item_a_remover]
                    salvar_json("itens.json", itens_atuais)
                    st.success(f"Item {item_a_remover} removido com sucesso!")
                    st.rerun()
        else:
            st.info("Não existem itens para remover.")

# --- 3. ESTRUTURA DE PRODUTOS (BOM) ---
elif menu_opcao == "Estrutura de Produtos (BOM)":
    st.header("Estrutura de Produtos")
    st.write("Associe componentes (SA ou MP) a um item pai (PA ou SA) para definir a árvore de fabrico.")
    
    itens = carregar_json("itens.json") or {}
    estrutura = carregar_json("estrutura.json") or {}
    
    if itens:
        with st.form("form_estrutura"):
            pais_disponiveis = [k for k, v in itens.items() if v.get("tipo") in ["PA", "SA"]]
            pai_escolhido = st.selectbox("Item Pai (PA ou SA)", pais_disponiveis, format_func=lambda x: f"{x} - {itens[x]['descricao']}")
            
            componente_escolhido = st.selectbox("Componente Necessário (SA ou MP)", list(itens.keys()), format_func=lambda x: f"{x} - {itens[x]['descricao']}")
            
            quantidade_nec = st.number_input("Quantidade do Componente por Unidade do Pai", min_value=0.01, value=1.0, step=0.1)
            
            adicionar_comp = st.form_submit_button("Adicionar Componente à Estrutura")
            
            if adicionar_comp:
                if pai_escolhido == componente_escolhido:
                    st.error("Um item não pode ser componente dele próprio!")
                else:
                    if not isinstance(estrutura, dict):
                        estrutura = {}
                    if pai_escolhido not in estrutura:
                        estrutura[pai_escolhido] = []
                    
                    # Evitar duplicados do mesmo componente no mesmo pai
                    estrutura[pai_escolhido] = [c for c in estrutura[pai_escolhido] if c.get("codigo_componente") != componente_escolhido]
                    
                    estrutura[pai_escolhido].append({
                        "codigo_componente": componente_escolhido,
                        "quantidade": float(quantidade_nec)
                    })
                    salvar_json("estrutura.json", estrutura)
                    st.success(f"Componente {componente_escolhido} adicionado com sucesso ao pai {pai_escolhido}!")
                    st.rerun()
        
        st.markdown("---")
        st.subheader("Estrutura Atual Registada no Sistema")
        if estrutura:
            for pai, comps in estrutura.items():
                st.markdown(f"**Item Pai: `{pai}`** ({itens.get(pai, {}).get('descricao', '')})")
                df_comps = pd.DataFrame(comps)
                st.dataframe(df_comps, use_container_width=True)
        else:
            st.info("Nenhuma estrutura de produtos registada ainda em `estrutura.json`.")
    else:
        st.warning("Cadastre itens primeiro para poder configurar a estrutura.")

# --- 4. ROTEIROS DE PRODUÇÃO ---
elif menu_opcao == "Roteiros de Produção":
    st.header("Roteiros de Fabrico")
    st.write("Defina as operações, centros de trabalho e tempos de fabrico para os itens produzidos.")
    
    itens = carregar_json("itens.json") or {}
    roteiros = carregar_json("roteiros.json") or {}
    
    if itens:
        with st.form("form_roteiros"):
            itens_fab = [k for k, v in itens.items() if v.get("tipo") in ["PA", "SA"]]
            item_rot = st.selectbox("Item Fabricado", itens_fab, format_func=lambda x: f"{x} - {itens[x]['descricao']}")
            
            operacao = st.text_input("Descrição da Operação (ex: Soldagem, Montagem, Pintura)")
            centro_trabalho = st.text_input("Centro de Trabalho (ex: CT-01, Bancada 2)")
            tempo_setup = st.number_input("Tempo de Setup (minutos)", min_value=0.0, value=10.0)
            tempo_operacao = st.number_input("Tempo por Unidade (minutos)", min_value=0.1, value=5.0)
            
            salvar_rot = st.form_submit_button("Guardar Roteiro")
            if salvar_rot:
                if operacao:
                    if not isinstance(roteiros, dict):
                        roteiros = {}
                    if item_rot not in roteiros:
                        roteiros[item_rot] = []
                        
                    roteiros[item_rot].append({
                        "operacao": operacao,
                        "centro_trabalho": centro_trabalho,
                        "tempo_setup": float(tempo_setup),
                        "tempo_operacao": float(tempo_operacao)
                    })
                    salvar_json("roteiros.json", roteiros)
                    st.success(f"Roteiro adicionado com sucesso para o item {item_rot}!")
                    st.rerun()
                else:
                    st.warning("Preencha a descrição da operação.")
                    
        st.markdown("---")
        st.subheader("Roteiros Atuais no Sistema")
        if roteiros:
            for item, ops in roteiros.items():
                st.markdown(f"**Item: `{item}`**")
                df_ops = pd.DataFrame(ops)
                st.dataframe(df_ops, use_container_width=True)
        else:
            st.info("Nenhum roteiro registado em `roteiros.json`.")
    else:
        st.warning("Cadastre itens para configurar roteiros.")

# --- 5. MOVIMENTAR ESTOQUE ---
elif menu_opcao == "Movimentar Estoque (Kardex)":
    st.header("Registar Movimentação de Estoque")
    
    itens = carregar_json("itens.json")
    if itens:
        with st.form("form_mov"):
            cod_selecionado = st.selectbox("Selecione o Item", list(itens.keys()), format_func=lambda x: f"{x} - {itens[x]['descricao']}")
            tipo_mov = st.selectbox("Tipo de Movimento", ["ENTRADA", "SAIDA", "AJUSTE"])
            qtd_mov = st.number_input("Quantidade", min_value=1, value=10)
            obs = st.text_input("Observação / Justificativa", value="Ajuste via Web")
            
            sub_mov = st.form_submit_button("Registar Movimentação")
            if sub_mov:
                with open(caminho_csv, "a", encoding="utf-8") as f:
                    f.write(f"{cod_selecionado},{tipo_mov},{int(qtd_mov)},{obs}\n")
                    
                st.success(f"Movimentação de {tipo_mov} ({qtd_mov} unidades) registada com sucesso para o item {cod_selecionado}!")
        
        st.markdown("---")
        st.subheader("Saldos Atuais Calculados pelo Sistema")
        for cod, item in itens.items():
            saldo = calcular_saldo_atual(cod)
            st.write(f"**{cod} - {item['descricao']}**: **{saldo} {item['unidade']}**")
    else:
        st.warning("Não existem itens cadastrados para movimentar.")

# --- 6. PLANO MESTRE (MPS) ---
elif menu_opcao == "Plano Mestre (MPS)":
    st.header("Plano Mestre de Produção (MPS)")
    st.write("Consulte, configure ou remova as demandas semanais (S1 a S8) para os Produtos Acabados (PA).")
    
    itens = carregar_json("itens.json") or {}
    pas_disponiveis = [k for k, v in itens.items() if str(v.get("tipo", "")).strip().upper() == "PA"]
    
    if pas_disponiveis:
        with st.form("form_mps"):
            st.subheader("Registar / Atualizar Demanda MPS para Produto Acabado")
            pa_escolhido = st.selectbox("Selecione o Produto Acabado (PA)", pas_disponiveis, format_func=lambda x: f"{x} - {itens[x]['descricao']}")
            
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1: s1 = st.number_input("Semana 1 (S1)", min_value=0, value=10)
            with col_s2: s2 = st.number_input("Semana 2 (S2)", min_value=0, value=15)
            with col_s3: s3 = st.number_input("Semana 3 (S3)", min_value=0, value=20)
            with col_s4: s4 = st.number_input("Semana 4 (S4)", min_value=0, value=0)
            
            col_s5, col_s6, col_s7, col_s8 = st.columns(4)
            with col_s5: s5 = st.number_input("Semana 5 (S5)", min_value=0, value=0)
            with col_s6: s6 = st.number_input("Semana 6 (S6)", min_value=0, value=0)
            with col_s7: s7 = st.number_input("Semana 7 (S7)", min_value=0, value=0)
            with col_s8: s8 = st.number_input("Semana 8 (S8)", min_value=0, value=0)
            
            col_b1, col_b2 = st.columns(2)
            salvar_mps_btn = col_b1.form_submit_button("Guardar / Atualizar MPS")
            apagar_mps_btn = col_b2.form_submit_button("Apagar MPS do Item Selecionado")
            
            if salvar_mps_btn:
                mps_atual = carregar_json("mps.json")
                if not isinstance(mps_atual, dict):
                    mps_atual = {}
                mps_atual[pa_escolhido] = {
                    "S1": int(s1), "S2": int(s2), "S3": int(s3), "S4": int(s4),
                    "S5": int(s5), "S6": int(s6), "S7": int(s7), "S8": int(s8)
                }
                salvar_json("mps.json", mps_atual)
                st.success(f"MPS atualizado com sucesso para o item {pa_escolhido}!")
                st.rerun()
                
            if apagar_mps_btn:
                mps_atual = carregar_json("mps.json")
                if isinstance(mps_atual, dict) and pa_escolhido in mps_atual:
                    del mps_atual[pa_escolhido]
                    salvar_json("mps.json", mps_atual)
                    st.success(f"MPS removido com sucesso para o item {pa_escolhido}!")
                    st.rerun()
                else:
                    st.warning("O item selecionado não possui registo no MPS.")
    else:
        st.warning("Não existem Produtos Acabados (PA) registados para configurar o MPS.")
    
    st.markdown("---")
    st.subheader("Plano Mestre Atual no Sistema")
    mps_data = carregar_json("mps.json")
    if mps_data:
        if isinstance(mps_data, dict):
            mps_lista = [{"Código PA": k, **v} for k, v in mps_data.items() if isinstance(v, dict)]
            df_mps = pd.DataFrame(mps_lista)
        else:
            df_mps = pd.DataFrame(mps_data)
        st.dataframe(df_mps, use_container_width=True)
    else:
        st.info("Nenhum dado de MPS encontrado.")

# --- 7. EXECUTAR MRP ---
elif menu_opcao == "Executar MRP":
    st.header("Motor de Cálculo MRP (Sequência RN04)")
    st.write("Processa o cálculo completo de necessidades (PA -> SA -> MP) respeitando o lead time, estoque de segurança e lote mínimo.")
    
    if st.button("Executar Motor MRP Real"):
        try:
            mrp.executar_mrp_geral()
            st.success("Cálculo MRP executado com sucesso através do motor oficial do backend!")
            
            ordens = carregar_json("ordens.json")
            if ordens:
                st.subheader("Ordens Resultantes do Cálculo")
                st.dataframe(pd.DataFrame(ordens), use_container_width=True)
            else:
                st.info("O cálculo foi concluído, mas nenhuma ordem foi gerada.")
        except Exception as e:
            st.error(f"Erro ao executar o cálculo MRP: {e}")

# --- 8. GRÁFICOS DE GESTÃO ---
elif menu_opcao == "Gráficos de Gestão":
    st.header("Indicadores Visuais de Estoque")
    itens = carregar_json("itens.json")
    if itens:
        codigos = list(itens.keys())
        saldos = [calcular_saldo_atual(c) for c in codigos]
        seguranca = [itens[c]["estoque_seguranca"] for c in codigos]
        
        fig, ax = plt.subplots(figsize=(10, 4))
        x = range(len(codigos))
        ax.bar(x, saldos, width=0.4, label="Saldo Atual", color="royalblue", align="center")
        ax.bar([p + 0.4 for p in x], seguranca, width=0.4, label="Est. Segurança", color="orange", align="center")
        ax.set_xticks([p + 0.2 for p in x])
        ax.set_xticklabels(codigos, rotation=45)
        ax.set_ylabel("Quantidade")
        ax.legend()
        st.pyplot(fig)