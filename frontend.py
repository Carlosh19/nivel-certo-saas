import streamlit as st
import requests
import pandas as pd
import uuid
import io
from supabase import create_client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

SUPABASE_URL = "https://hzpmzxtpozifbkzjffkq.supabase.co"
SUPABASE_KEY = "sb_publishable_Nguzd6BG38Ztw4MjhjRZlg_K31XGf1X"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL da API em produção (Render)
API_URL = "https://nivel-certo-saas.onrender.com"

st.set_page_config(page_title="Nível Certo - Sistema", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFBF8; } 
    h1, h2, h3, h4, h5, h6, p, label, .st-emotion-cache-10trblm { color: #2E1A0F !important; } 
    .stButton>button { background-color: #A67C43; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #8C6430; color: white; }
    
    [data-testid="stSidebar"] { 
        background-color: #F2EBE1; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    div[data-testid="stAlert"] { background-color: #2E1A0F !important; border: 1px solid #D4AF37 !important; }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] div, div[data-testid="stAlert"] svg { color: #D4AF37 !important; font-weight: 500; }
    
    .dash-box { border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; text-align: center; background-color: #ffffff; }
    .dash-title { font-size: 12px; font-weight: bold; color: #2E1A0F; text-transform: uppercase; }
    .dash-value { font-size: 28px; font-weight: bold; margin: 10px 0; color: #0066cc; }
    .dash-sub { font-size: 12px; color: #666666; }
    .val-green { color: #2e7d32; }
    .val-red { color: #c62828; }
    .val-orange { color: #e65100; }

    /* ESTILIZAÇÃO COMPLETA DAS TABELAS: Fundo Marrom Escuro, Letras Douradas e Conteúdo Centralizado */
    [data-testid="stDataFrame"] {
        background-color: #2E1A0F !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 8px;
    }
    
    [data-testid="stDataFrame"] th {
        background-color: #1F1109 !important;
        color: #D4AF37 !important;
        text-align: center !important;
        font-weight: bold !important;
    }
    
    [data-testid="stDataFrame"] td {
        background-color: #2E1A0F !important;
        color: #D4AF37 !important;
        text-align: center !important;
    }
    
    [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span {
        text-align: center !important;
        color: #D4AF37 !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    try:
        user_response = supabase.auth.get_user()
        if user_response and user_response.user:
            st.session_state.usuario = user_response.user
    except Exception:
        pass

def fazer_login(email, senha):
    try:
        resposta = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        st.session_state.usuario = resposta.user
        st.rerun()
    except Exception:
        st.error("Erro no login: Verifique os seus dados.")

def gerar_pdf_projeto(proj):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "NÍVEL CERTO - RELATÓRIO EXECUTIVO DE PROJETO")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, "Controle Financeiro e Conclusão de Obra")
    p.line(50, height - 80, width - 50, height - 80)
    
    y = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"ID do Projeto: {proj.get('id_projeto_txt')}")
    
    y -= 30
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Cliente: {proj.get('cliente_nome')}")
    y -= 20
    p.drawString(50, y, f"Ambiente: {proj.get('ambiente')}")
    y -= 20
    p.drawString(50, y, f"Data de Início: {proj.get('data_inicio')}")
    y -= 20
    p.drawString(50, y, f"Valor do Contrato: R$ {proj.get('valor_contrato', 0):,.2f}")
    y -= 20
    p.drawString(50, y, f"Valor Recebido: R$ {proj.get('valor_recebido', 0):,.2f}")
    y -= 20
    p.drawString(50, y, f"Status da Obra: {proj.get('status_projeto')}")
    y -= 20
    p.drawString(50, y, f"Status Financeiro: {proj.get('status_pagamento')}")
    
    y -= 50
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Este documento atesta que o projeto acima foi concluído e liquidado com sucesso.")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

if st.session_state.usuario is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try: st.image("Logo.png", use_container_width=True)
        except: 
            try: st.image("Logo.jpeg", use_container_width=True)
            except: pass
                
        st.title("Gestão Nível Certo")
        email_login = st.text_input("E-mail")
        senha_login = st.text_input("Palavra-passe", type="password")
        if st.button("Entrar"):
            fazer_login(email_login, senha_login)
else:
    # ---------------- BARRA LATERAL (SIDEBAR) ----------------
    with st.sidebar:
        try: st.image("Logo.png", use_container_width=True)
        except: 
            try: st.image("Logo.jpeg", use_container_width=True)
            except: pass
        
        st.markdown("---")
        
        menu = st.radio(
            "Navegação", 
            ["📊 PAINEL GERAL", "🪵 PROJETOS & RECEITAS", "💸 CUSTOS & DESPESAS", "👥 BASE DE CLIENTES", "⚙️ ADMINISTRAÇÃO"],
            label_visibility="collapsed"
        )
        
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"**👤 Logado:**\n`{st.session_state.usuario.email}`")
        
        col_sair1, col_sair2 = st.columns([1, 1])
        with col_sair2:
            if st.button("Sair"):
                supabase.auth.sign_out()
                st.session_state.update(usuario=None)
                st.rerun()

    # BUSCAR DADOS DA API NA NUVEM
    try:
        clientes = requests.get(f"{API_URL}/clientes").json()
        projetos = requests.get(f"{API_URL}/projetos").json()
        despesas = requests.get(f"{API_URL}/despesas").json()
        if isinstance(clientes, dict) and "erro" in clientes: clientes = []
        if isinstance(projetos, dict) and "erro" in projetos: projetos = []
        if isinstance(despesas, dict) and "erro" in despesas: despesas = []
    except:
        clientes, projetos, despesas = [], [], []

    # ---------------- CONTEÚDO DAS PÁGINAS ----------------
    
    if menu == "📊 PAINEL GERAL":
        st.title("📊 PAINEL GERAL • Visão Executiva")
        df_proj = pd.DataFrame(projetos) if projetos else pd.DataFrame()
        df_desp = pd.DataFrame(despesas) if despesas else pd.DataFrame()

        fat_total = df_proj["valor_contrato"].sum() if not df_proj.empty and "valor_contrato" in df_proj.columns else 0
        recebido = df_proj["valor_recebido"].sum() if not df_proj.empty and "valor_recebido" in df_proj.columns else 0
        
        custos_desp_material = df_desp["valor_total"].sum() if not df_desp.empty and "valor_total" in df_desp.columns else 0
        custos_desp_mao = df_desp["mao_de_obra"].sum() if not df_desp.empty and "mao_de_obra" in df_desp.columns else 0
        
        custo_total = custos_desp_mao + custos_desp_material
        
        lucro = fat_total - custo_total
        margem = (lucro / fat_total * 100) if fat_total > 0 else 0
        saldo_receber = fat_total - recebido

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""<div class='dash-box'><div class='dash-title'>FATURAMENTO CONTRATADO</div><div class='dash-value'>R$ {fat_total:,.2f}</div><div class='dash-sub'>Recebido: R$ {recebido:,.2f}</div></div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class='dash-box'><div class='dash-title'>CUSTOS TOTAIS DA OPERAÇÃO</div><div class='dash-value val-red'>R$ {custo_total:,.2f}</div><div class='dash-sub'>Mão de Obra + Materiais (Despesas)</div></div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class='dash-box'><div class='dash-title'>LUCRO OPERACIONAL ESTIMADO</div><div class='dash-value val-green'>R$ {lucro:,.2f}</div><div class='dash-sub'>Margem Líquida: {margem:.0f}%</div></div>""", unsafe_allow_html=True)
        c4.markdown(f"""<div class='dash-box'><div class='dash-title'>SALDO A RECEBER (CLIENTES)</div><div class='dash-value val-orange'>R$ {saldo_receber:,.2f}</div><div class='dash-sub'>Em aberto para liquidação</div></div>""", unsafe_allow_html=True)

        st.write("---")
        col_res_proj, col_res_desp = st.columns(2)
        
        with col_res_proj:
            st.markdown("### 📊 Resumo e Histórico de Projetos")
            if not df_proj.empty:
                df_proj["débitos a receber"] = df_proj["valor_contrato"] - df_proj["valor_recebido"]
                df_resumo_projetos = df_proj[["cliente_nome", "valor_contrato", "débitos a receber", "status_projeto", "status_pagamento"]]
                st.dataframe(df_resumo_projetos, use_container_width=True, hide_index=True, column_config={"cliente_nome": "Cliente", "valor_contrato": st.column_config.NumberColumn("Valor Contrato", format="R$ %.2f"), "débitos a receber": st.column_config.NumberColumn("Débitos a Receber", format="R$ %.2f"), "status_projeto": "Status do Projeto", "status_pagamento": "Status Pagamento"})
            else:
                st.info("Nenhum projeto lançado.")
                
        with col_res_desp:
            st.markdown("### 💸 Detalhamento de Insumos e Despesas")
            if not df_desp.empty:
                colunas_mostrar = [c for c in ["mao_de_obra", "descricao", "valor_total", "status_pagamento"] if c in df_desp.columns]
                df_resumo_desp = df_desp[colunas_mostrar].rename(columns={
                    "mao_de_obra": "Custo da Mão de Obra",
                    "descricao": "Fornecedor de material",
                    "valor_total": "Valor total gasto de material",
                    "status_pagamento": "Status Pagamento"
                })
                st.dataframe(
                    df_resumo_desp, 
                    use_container_width=True, 
                    hide_index=True, 
                    column_config={
                        "Custo da Mão de Obra": st.column_config.NumberColumn("Custo da Mão de Obra", format="R$ %.2f"),
                        "Fornecedor de material": "Fornecedor de material",
                        "Valor total gasto de material": st.column_config.NumberColumn("Valor total gasto de material", format="R$ %.2f"),
                        "Status Pagamento": "Status Pagamento"
                    }
                )
            else:
                st.info("Nenhuma despesa lançada.")

    elif menu == "🪵 PROJETOS & RECEITAS":
        st.title("🪵 PROJETOS & RECEITAS")
        aba_novo, aba_editar = st.tabs(["➕ Lançar Novo Projeto", "✏️ Atualizar Status e Valores"])
        
        with aba_novo:
            c_form, c_table = st.columns([1, 2.5])
            with c_form:
                st.subheader("Novo Projeto")
                id_gerado = f"NVC-{str(uuid.uuid4())[:4].upper()}"
                st.text_input("ID do Projeto", value=id_gerado, disabled=True)
                cliente_nome = st.text_input("Nome do Cliente")
                ambiente = st.text_input("Ambiente (ex: Cozinha)")
                data_inicio = st.date_input("Data de Início", format="DD/MM/YYYY").strftime("%Y-%m-%d")
                
                valor_c = st.number_input("Valor Contrato (R$)", min_value=0.0, step=100.0)
                valor_r = st.number_input("Sinal Recebido (R$)", min_value=0.0, step=100.0)
                status_p = st.selectbox("Status da Obra", ["Aguardando Insumos", "Em Produção", "Em Montagem", "Finalizado"])
                status_pag = st.selectbox("Status Financeiro", ["Em Aberto", "Parcial", "Quitado"])
                
                if st.button("Guardar Projeto"):
                    if cliente_nome:
                        cliente_existe = next((c for c in clientes if c['nome'].lower() == cliente_nome.lower()), None)
                        if not cliente_existe: requests.post(f"{API_URL}/clientes", json={"nome": cliente_nome, "email": "", "telefone": "", "endereco": ""})
                        
                        dados_proj = {
                            "id_projeto_txt": id_gerado, "cliente_nome": cliente_nome, "ambiente": ambiente, 
                            "data_inicio": data_inicio, "valor_contrato": valor_c, "valor_recebido": valor_r, 
                            "status_projeto": status_p, "status_pagamento": status_pag
                        }
                        res_post = requests.post(f"{API_URL}/projetos", json=dados_proj)
                        if res_post.status_code == 200 and "erro" not in res_post.json():
                            st.success("Projeto criado!")
                            st.rerun()
                        else: st.error("Erro ao guardar.")
                    else: st.error("O Nome do Cliente é obrigatório.")
                        
            with c_table:
                st.subheader("Lista Geral de Obras")
                if projetos:
                    df2 = pd.DataFrame(projetos)
                    df2["data_inicio"] = pd.to_datetime(df2["data_inicio"]).dt.strftime('%d/%m/%Y')
                    st.dataframe(df2[["id_projeto_txt", "cliente_nome", "data_inicio", "valor_contrato", "valor_recebido", "status_projeto", "status_pagamento"]], use_container_width=True, hide_index=True)
                else: st.info("Nenhum projeto lançado.")

        with aba_editar:
            st.subheader("Atualizar Status, Recebimentos e Emitir PDF")
            if projetos:
                opcoes_p_edit = {f"{p['id_projeto_txt']} - {p['cliente_nome']} ({p['ambiente']})": p for p in projetos}
                proj_selec_nome = st.selectbox("Selecione o Projeto", list(opcoes_p_edit.keys()))
                proj_dados = opcoes_p_edit[proj_selec_nome]
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    novo_status_obra = st.selectbox("Atualizar Status da Obra", ["Aguardando Insumos", "Em Produção", "Em Montagem", "Finalizado"], index=["Aguardando Insumos", "Em Produção", "Em Montagem", "Finalizado"].index(proj_dados.get("status_projeto", "Aguardando Insumos")))
                    novo_status_pag = st.selectbox("Atualizar Status Financeiro", ["Em Aberto", "Parcial", "Quitado"], index=["Em Aberto", "Parcial", "Quitado"].index(proj_dados.get("status_pagamento", "Em Aberto")))
                with col_e2:
                    novo_valor_recebido = st.number_input("Atualizar Valor Recebido (R$)", value=float(proj_dados.get("valor_recebido", 0.0)), step=100.0)
                    st.markdown(f"**Valor Contrato Total:** R$ {proj_dados.get('valor_contrato', 0):,.2f}")
                    st.markdown(f"**Saldo Restante:** R$ {proj_dados.get('valor_contrato', 0) - novo_valor_recebido:,.2f}")
                
                if st.button("Salvar Atualizações do Projeto"):
                    dados_atualizados = {
                        "id_projeto_txt": proj_dados["id_projeto_txt"],
                        "cliente_nome": proj_dados["cliente_nome"],
                        "ambiente": proj_dados["ambiente"],
                        "data_inicio": proj_dados["data_inicio"],
                        "valor_contrato": proj_dados["valor_contrato"],
                        "valor_recebido": novo_valor_recebido,
                        "status_projeto": novo_status_obra,
                        "status_pagamento": novo_status_pag
                    }
                    res_put = requests.put(f"{API_URL}/projetos/{proj_dados['id_projeto_txt']}", json=dados_atualizados)
                    if res_put.status_code == 200:
                        st.success("Projeto atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar projeto.")

                if proj_dados.get("status_projeto") == "Finalizado" and proj_dados.get("status_pagamento") == "Quitado":
                    st.success("🎉 Este projeto encontra-se Finalizado e Quitado! Pode descarregar o relatório executivo em PDF abaixo:")
                    pdf_file = gerar_pdf_projeto(proj_dados)
                    st.download_button(
                        label="📄 Descarregar Relatório PDF do Projeto",
                        data=pdf_file,
                        file_name=f"Projeto_{proj_dados['id_projeto_txt']}_{proj_dados['cliente_nome']}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.info("Nenhum projeto disponível para editar.")

    elif menu == "💸 CUSTOS & DESPESAS":
        st.title("💸 CUSTOS & DESPESAS")
        c_form_d, c_table_d, c_delete_d = st.columns([1, 2, 1])
        with c_form_d:
            st.subheader("Lançar Nova Despesa")
            opcoes_proj = ["Nenhum / Custo Fixo"] + [f"{p['id_projeto_txt']} - {p['cliente_nome']}" for p in projetos]
            proj_vinc = st.selectbox("Vincular ao Projeto (Opcional)", opcoes_proj)
            data_lanc = st.date_input("Data de Lançamento", format="DD/MM/YYYY").strftime("%Y-%m-%d")
            
            mao_obra_despesa = st.number_input("Custo da Mão de Obra (R$)", min_value=0.0, step=10.0)
            descricao = st.text_input("Fornecedor de material")
            forma_pag = st.selectbox("Forma de Pagamento", ["PIX", "Cartão", "Boleto", "Dinheiro"])
            v_total = st.number_input("Valor total gasto de material (R$)", min_value=0.0, step=10.0)
            status_pg = st.selectbox("Status", ["Pago", "Pendente"])
            
            if st.button("Registar Despesa"):
                id_proj_salvar = proj_vinc.split(" - ")[0] if proj_vinc != "Nenhum / Custo Fixo" else ""
                dados_d = {
                    "data_lancamento": data_lanc, "mao_de_obra": mao_obra_despesa, 
                    "descricao": descricao, "forma_pagamento": forma_pag, "valor_total": v_total, 
                    "status_pagamento": status_pg, "projeto_vinculado": id_proj_salvar
                }
                res_post_d = requests.post(f"{API_URL}/despesas", json=dados_d)
                if res_post_d.status_code == 200 and "erro" not in res_post_d.json():
                    st.success("Despesa registada!")
                    st.rerun()
                else: st.error("Erro ao registar.")

        with c_table_d:
            st.subheader("Controle de Custos")
            if despesas:
                df_d = pd.DataFrame(despesas)
                df_d["data_lancamento"] = pd.to_datetime(df_d["data_lancamento"]).dt.strftime('%d/%m/%Y')
                colunas_tabela_d = [c for c in ["data_lancamento", "projeto_vinculado", "mao_de_obra", "descricao", "valor_total", "status_pagamento"] if c in df_d.columns]
                df_tabela_exibicao = df_d[colunas_tabela_d].rename(columns={
                    "data_lancamento": "Data", "projeto_vinculado": "Projeto Vinculado",
                    "mao_de_obra": "Custo da Mão de Obra", "descricao": "Fornecedor de material",
                    "valor_total": "Valor total gasto de material", "status_pagamento": "Status Pagamento"
                })
                st.dataframe(df_tabela_exibicao, use_container_width=True, hide_index=True)
            else: st.info("Nenhuma despesa registada.")

        with c_delete_d:
            st.subheader("Excluir Despesa")
            if despesas:
                opcoes_despesas = {f"[{d.get('data_lancamento', '')}] Fornecedor: {d.get('descricao', '')} - Material: R$ {d.get('valor_total', 0)}": d['id'] for d in despesas}
                desp_selecionada = st.selectbox("Selecione para excluir", list(opcoes_despesas.keys()))
                if st.button("Apagar Despesa", type="primary"):
                    id_desp_apagar = opcoes_despesas[desp_selecionada]
                    requests.delete(f"{API_URL}/despesas/{id_desp_apagar}")
                    st.success("Apagado.")
                    st.rerun()
            else: st.info("Sem despesas.")

    elif menu == "👥 BASE DE CLIENTES":
        st.title("👥 BASE DE CLIENTES")
        if clientes:
            c_edit, c_view, c_delete = st.columns([1, 2, 1])
            opcoes_cli = {c['nome']: c for c in clientes}
            with c_edit:
                st.markdown("**Editar Cliente**")
                cli_selecionado = st.selectbox("Selecione para editar", list(opcoes_cli.keys()))
                cli_dados = opcoes_cli[cli_selecionado]
                novo_tel = st.text_input("Telefone", value=cli_dados.get("telefone", ""))
                novo_email = st.text_input("E-mail", value=cli_dados.get("email", ""))
                novo_end = st.text_input("Endereço", value=cli_dados.get("endereco", ""))
                if st.button("Atualizar Ficha"):
                    requests.put(f"{API_URL}/clientes/{cli_dados['id']}", json={"nome": cli_selecionado, "email": novo_email, "telefone": novo_tel, "endereco": novo_end})
                    st.success("Atualizado!")
                    st.rerun()
            with c_view:
                st.markdown("**Contatos**")
                st.dataframe(pd.DataFrame(clientes)[["nome", "telefone", "email", "endereco"]], use_container_width=True, hide_index=True)
            with c_delete:
                st.markdown("**Excluir Cliente**")
                cli_del_selecionado = st.selectbox("Selecione para excluir", list(opcoes_cli.keys()), key="del_cli")
                if st.button("Excluir Cliente", type="primary"):
                    id_para_deletar = opcoes_cli[cli_del_selecionado]['id']
                    requests.delete(f"{API_URL}/clientes/{id_para_deletar}")
                    st.success("Excluído.")
                    st.rerun()
        else: st.info("Base vazia.")

    elif menu == "⚙️ ADMINISTRAÇÃO":
        st.title("⚙️ ADMINISTRAÇÃO")
        st.markdown("Crie novos utilizadores para o sistema.")
        col_admin, col_vazia = st.columns([1,2])
        with col_admin:
            novo_admin_email = st.text_input("E-mail do Novo Usuário")
            novo_admin_senha = st.text_input("Palavra-passe", type="password")
            if st.button("Criar Acesso ao Sistema"):
                if novo_admin_email and len(novo_admin_senha) >= 6:
                    try:
                        resp = supabase.auth.sign_up({"email": novo_admin_email, "password": novo_admin_senha})
                        if resp.user: st.success("Acesso criado com sucesso!")
                    except Exception as e: st.error(f"Erro: {str(e)}")
                else: st.warning("Preencha corretamente.")