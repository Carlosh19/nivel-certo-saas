import random
import pandas as pd
import streamlit as st
from supabase import create_client

# Configuração da página
st.set_page_config(
    page_title="Gestão Nível Certo", page_icon="🪵", layout="wide"
)

# Credenciais do Supabase
SUPABASE_URL = "https://hzpmzxtpozifbkzjffkq.supabase.co"
SUPABASE_KEY = "sb_publishable_Nguzd6BG38Ztw4MjhjRZlg_K31XGf1X"


@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

# --- ESTADO DE SESSÃO DE AUTENTICAÇÃO ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

# --- TELA DE LOGIN ---
if not st.session_state.autenticado:
  st.markdown("<h1 style='text-align: center;'>Gestão Nível Certo</h1>", unsafe_allow_html=True)
  st.markdown("<h3 style='text-align: center; color: gray;'>Painel de Controlo Exclusivo - 100% MDF</h3>", unsafe_allow_html=True)
  
  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    email_input = st.text_input("E-mail", value="carlos.diference@gmail.com")
    senha_input = st.text_input("Palavra-passe", type="password")

    if st.button("Entrar", use_container_width=True):
      if email_input == "carlos.diference@gmail.com" and senha_input == "teste123456":
        st.session_state.autenticado = True
        st.session_state.usuario = {"nome": "Carlos", "email": email_input}
        st.rerun()
      else:
        try:
          resposta = (
              supabase.table("usuarios")
              .select("*")
              .eq("email", email_input)
              .execute()
          )
          if resposta.data:
            st.session_state.autenticado = True
            st.session_state.usuario = resposta.data[0]
            st.rerun()
          else:
            st.error("E-mail ou palavra-passe incorretos.")
        except Exception:
          st.error("Erro ao validar credenciais. Verifique a base de dados.")

else:
  # --- MENU LATERAL (SIDEBAR) ---
  st.sidebar.title("Menu Nível Certo")
  
  menu_opcao = st.sidebar.radio(
      "Navegação",
      ["📊 Painel Geral", "🪵 Projetos & Receitas", "💰 Custos & Despesas", "👥 Base de Clientes", "⚙️ Administração"]
  )

  st.sidebar.markdown("---")
  st.sidebar.text(f"Logado: {st.session_state.get('usuario', {}).get('email', 'Carlos')}")
  if st.sidebar.button("Terminar Sessão", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

  # --- 1. PAINEL GERAL ---
  if menu_opcao == "📊 Painel Geral":
    st.title("📊 Painel Geral - Nível Certo")
    st.write("Indicadores de desempenho e resumo financeiro dos projetos em 100% MDF.")
    
    try:
      res_proj = supabase.table("projetos").select("*").execute()
      df_proj = pd.DataFrame(res_proj.data) if res_proj.data else pd.DataFrame()
      
      total_projetos = len(df_proj) if not df_proj.empty else 0
      faturamento_total = df_proj["valor_contrato"].sum() if not df_proj.empty and "valor_contrato" in df_proj.columns else 0.0
      recebido_total = df_proj["valor_recebido"].sum() if not df_proj.empty and "valor_recebido" in df_proj.columns else 0.0

      col1, col2, col3 = st.columns(3)
      with col1:
        st.metric(label="Projetos Ativos", value=str(total_projetos))
      with col2:
        st.metric(label="Valor Total Contratado", value=f"R$ {faturamento_total:,.2f}")
      with col3:
        st.metric(label="Valor Já Recebido", value=f"R$ {recebido_total:,.2f}")

      st.markdown("---")
      st.subheader("Projetos Recentes")
      if not df_proj.empty:
        st.dataframe(df_proj, use_container_width=True)
      else:
        st.info("Nenhum projeto registado ainda.")
    except Exception as e:
      st.warning(f"Aviso ao carregar dados do Supabase: {e}")

  # --- 2. PROJETOS & RECEITAS ---
  elif menu_opcao == "🪵 Projetos & Receitas":
    st.title("🪵 Gestão de Projetos 3D & Receitas")
    st.write("Registe novos projetos, atualize pagamentos e conclua entregas.")

    tab_novo, tab_edita = st.tabs(["➕ Adicionar Novo Projeto", "✏️ Atualizar / Concluir Projeto"])

    with tab_novo:
      id_gerado = f"NVC-{random.randint(1000, 9999)}"
      with st.form("form_novo_projeto"):
        st.info(f"🔑 Código do Projeto Gerado Automaticamente: **{id_gerado}**")
        
        col1, col2 = st.columns(2)
        with col1:
          cliente = st.text_input("Nome do Cliente")
          ambiente = st.text_input("Ambiente (ex: Cozinha, Closet)")
        with col2:
          marcenaria = st.text_input("Marcenaria / Marceneiro Responsável")
          valor_c = st.number_input("Valor do Contrato (R$)", min_value=0.0, step=100.0)
          valor_r = st.number_input("Valor Já Recebido (R$)", min_value=0.0, step=100.0)
        
        status = st.selectbox("Status do Projeto", ["Aguardando Insumos", "Em Fabricação", "Em Montagem", "Concluído e Entregue - 100% Pago"])
        
        submitted = st.form_submit_button("Guardar Projeto")
        if submitted:
          try:
            supabase.table("projetos").insert({
                "id_projeto_txt": id_gerado,
                "cliente_nome": cliente,
                "ambiente": ambiente,
                "marcenaria": marcenaria,
                "valor_contrato": valor_c,
                "valor_recebido": valor_r,
                "status_projeto": status
            }).execute()
            st.success(f"Projeto {id_gerado} guardado com sucesso!")
            st.rerun()
          except Exception as err:
            st.error(f"Erro ao guardar projeto: {err}")

    with tab_edita:
      st.subheader("Atualizar Dados, Pagamentos ou Concluir Projeto")
      try:
        res_p = supabase.table("projetos").select("*").execute()
        if res_p.data:
          df_p = pd.DataFrame(res_p.data)
          # Criar lista de seleção com ID e Cliente
          lista_projetos = [f"{row['id_projeto_txt']} - {row['cliente_nome']} ({row['ambiente']})" for index, row in df_p.iterrows()]
          escolha_p = st.selectbox("Selecione o Projeto para Editar", lista_projetos)
          
          if escolha_p:
            id_selecionado = escolha_p.split(" - ")[0]
            proj_atual = df_p[df_p["id_projeto_txt"] == id_selecionado].iloc[0]
            
            with st.form("form_edita_projeto"):
              c1, c2 = st.columns(2)
              with c1:
                novo_cliente = st.text_input("Nome do Cliente", value=str(proj_atual.get("cliente_nome", "")))
                novo_ambiente = st.text_input("Ambiente", value=str(proj_atual.get("ambiente", "")))
                nova_marcenaria = st.text_input("Marcenaria Responsável", value=str(proj_atual.get("marcenaria", "")))
              with c2:
                novo_val_c = st.number_input("Valor do Contrato (R$)", value=float(proj_atual.get("valor_contrato", 0.0)), step=100.0)
                novo_val_r = st.number_input("Valor Recebido (R$)", value=float(proj_atual.get("valor_recebido", 0.0)), step=100.0)
                
                status_atuais = ["Aguardando Insumos", "Em Fabricação", "Em Montagem", "Concluído e Entregue - 100% Pago"]
                status_atual_db = proj_atual.get("status_projeto", "Aguardando Insumos")
                idx_status = status_atuais.index(status_atual_db) if status_atual_db in status_atuais else 0
                novo_status = st.selectbox("Status do Projeto", status_atuais, index=idx_status)

              btn_atualiza_proj = st.form_submit_button("Atualizar / Salvar Alterações do Projeto")
              if btn_atualiza_proj:
                try:
                  supabase.table("projetos").update({
                      "cliente_nome": novo_cliente,
                      "ambiente": novo_ambiente,
                      "marcenaria": nova_marcenaria,
                      "valor_contrato": novo_val_c,
                      "valor_recebido": novo_val_r,
                      "status_projeto": novo_status
                  }).eq("id_projeto_txt", id_selecionado).execute()
                  st.success(f"Projeto {id_selecionado} atualizado com sucesso!")
                  st.rerun()
                except Exception as err_up:
                  st.error(f"Erro ao atualizar projeto: {err_up}")
        else:
          st.info("Nenhum projeto registado para editar.")
      except Exception as e:
        st.warning(f"Erro ao carregar projetos: {e}")

    st.markdown("---")
    st.subheader("Lista Geral de Projetos Existentes")
    try:
      res = supabase.table("projetos").select("*").execute()
      if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
      else:
        st.info("Nenhum projeto registado.")
    except Exception:
      st.info("Tabela de projetos em configuração.")

  # --- 3. CUSTOS & DESPESAS ---
  elif menu_opcao == "💰 Custos & Despesas":
    st.title("💰 Controlo de Custos & Despesas")
    st.write("Registo do valor total de insumos e custos operacionais.")

    with st.expander("➕ Registar Nova Despesa / Custo"):
      with st.form("form_despesa"):
        descricao = st.text_input("Descrição do Custo / Insumos (ex: Insumos Projeto Cozinha Gabriel)")
        valor_custo = st.number_input("Valor Total (R$)", min_value=0.0, step=50.0)
        data_custo = st.date_input("Data")

        btn_custo = st.form_submit_button("Guardar Despesa")
        if btn_custo:
          try:
            supabase.table("despesas").insert({
                "descricao": descricao,
                "valor": valor_custo,
                "data": str(data_custo)
            }).execute()
            st.success("Despesa registada com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao guardar despesa: {e}")

    st.markdown("---")
    st.subheader("Registo de Despesas")
    try:
      res_c = supabase.table("despesas").select("*").execute()
      if res_c.data:
        st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)
      else:
        st.info("Nenhuma despesa registada ainda.")
    except Exception as e:
      st.warning(f"Erro ao consultar a tabela 'despesas': {e}")

  # --- 4. BASE DE CLIENTES ---
  elif menu_opcao == "👥 Base de Clientes":
    st.title("👥 Base de Clientes")
    st.write("Gestão de contactos, moradas e histórico de atendimento.")

    tab_cad_cli, tab_edit_cli = st.tabs(["➕ Cadastrar Novo Cliente", "✏️ Editar / Atualizar Cliente"])

    with tab_cad_cli:
      with st.form("form_cliente"):
        nome_cli = st.text_input("Nome Completo")
        tel_cli = st.text_input("Telefone / WhatsApp")
        email_cli = st.text_input("E-mail do Cliente")
        obs_cli = st.text_area("Observações / Endereço")

        btn_cli = st.form_submit_button("Cadastrar Cliente")
        if btn_cli:
          try:
            supabase.table("clientes").insert({
                "nome": nome_cli,
                "telefone": tel_cli,
                "email": email_cli,
                "observacoes": obs_cli
            }).execute()
            st.success("Cliente cadastrado com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao cadastrar cliente: {e}")

    with tab_edit_cli:
      st.subheader("Editar Informações de um Cliente")
      try:
        res_cli_all = supabase.table("clientes").select("*").execute()
        if res_cli_all.data:
          df_cli = pd.DataFrame(res_cli_all.data)
          lista_clientes = [f"{row['id']} - {row['nome']}" for index, row in df_cli.iterrows()]
          escolha_cli = st.selectbox("Selecione o Cliente para Editar", lista_clientes)
          
          if escolha_cli:
            id_cli_sel = int(escolha_cli.split(" - ")[0])
            cli_atual = df_cli[df_cli["id"] == id_cli_sel].iloc[0]
            
            with st.form("form_edita_cliente"):
              ec1, ec2 = st.columns(2)
              with ec1:
                e_nome = st.text_input("Nome Completo", value=str(cli_atual.get("nome", "")))
                e_tel = st.text_input("Telefone / WhatsApp", value=str(cli_atual.get("telefone", "")))
              with ec2:
                e_email = st.text_input("E-mail", value=str(cli_atual.get("email", "")))
                e_end = st.text_input("Endereço / Observações", value=str(cli_atual.get("observacoes", "")))
              
              btn_salva_cli = st.form_submit_button("Salvar Alterações do Cliente")
              if btn_salva_cli:
                try:
                  supabase.table("clientes").update({
                      "nome": e_nome,
                      "telefone": e_tel,
                      "email": e_email,
                      "observacoes": e_end
                  }).eq("id", id_cli_sel).execute()
                  st.success("Informações do cliente atualizadas com sucesso!")
                  st.rerun()
                except Exception as err_cli:
                  st.error(f"Erro ao atualizar cliente: {err_cli}")
        else:
          st.info("Nenhum cliente registado para editar.")
      except Exception as ex_c:
        st.warning(f"Erro ao carregar clientes: {ex_c}")

    st.markdown("---")
    st.subheader("Clientes Cadastrados")
    try:
      res_cli = supabase.table("clientes").select("*").execute()
      if res_cli.data:
        st.dataframe(pd.DataFrame(res_cli.data), use_container_width=True)
      else:
        st.info("Nenhum cliente cadastrado.")
    except Exception:
      st.info("Tabela 'clientes' pendente de criação no Supabase.")

  # --- 5. ADMINISTRAÇÃO ---
  elif menu_opcao == "⚙️ Administração":
    st.title("⚙️ Administração do Sistema")
    st.write("Gestão de utilizadores e acessos.")

    with st.expander("➕ Adicionar Novo Utilizador / Sócio ao Sistema"):
      with st.form("form_usuario"):
        novo_email = st.text_input("E-mail de Acesso")
        nova_senha = st.text_input("Palavra-passe", type="password")
        perfil_user = st.selectbox("Perfil", ["Sócio / Administrador", "Parceiro / Operacional"])

        btn_user = st.form_submit_button("Criar Utilizador")
        if btn_user:
          try:
            supabase.table("usuarios").insert({
                "email": novo_email,
                "senha": nova_senha,
                "perfil": perfil_user
            }).execute()
            st.success(f"Utilizador {novo_email} criado com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao criar utilizador: {e}")

    st.markdown("---")
    st.subheader("Utilizadores com Acesso ao Sistema")
    try:
      res_u = supabase.table("usuarios").select("*").execute()
      if res_u.data:
        st.dataframe(pd.DataFrame(res_u.data), use_container_width=True)
      else:
        st.info("Apenas o administrador padrão configurado.")
    except Exception:
      st.info("Tabela 'usuarios' pronta para uso.")