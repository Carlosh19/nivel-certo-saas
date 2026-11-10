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
      st.subheader("Lista de Projetos Recentes")
      if not df_proj.empty:
        st.dataframe(df_proj, use_container_width=True)
      else:
        st.info("Nenhum projeto registado ainda.")
    except Exception as e:
      st.warning("Aviso: Conectado ao Supabase, mas as tabelas ainda precisam de estar criadas para exibir os indicadores.")

  # --- 2. PROJETOS & RECEITAS ---
  elif menu_opcao == "🪵 Projetos & Receitas":
    st.title("🪵 Gestão de Projetos 3D & Receitas")
    st.write("Registe novos projetos, atualize valores e acompanhe o status de execução.")

    with st.expander("➕ Adicionar Novo Projeto", expanded=True):
      with st.form("form_novo_projeto"):
        col1, col2 = st.columns(2)
        with col1:
          id_proj = st.text_input("Código do Projeto (ex: NVC-8162)")
          cliente = st.text_input("Nome do Cliente")
          ambiente = st.text_input("Ambiente (ex: Cozinha, Closet)")
        with col2:
          valor_c = st.number_input("Valor do Contrato (R$)", min_value=0.0, step=100.0)
          valor_r = st.number_input("Valor Recebido (R$)", min_value=0.0, step=100.0)
          status = st.selectbox("Status do Projeto", ["Aguardando Insumos", "Em Fabricação", "Em Montagem", "Concluído"])
        
        submitted = st.form_submit_button("Guardar Projeto")
        if submitted:
          try:
            supabase.table("projetos").insert({
                "id_projeto_txt": id_proj,
                "cliente_nome": cliente,
                "ambiente": ambiente,
                "valor_contrato": valor_c,
                "valor_recebido": valor_r,
                "status_projeto": status
            }).execute()
            st.success("Projeto guardado com sucesso no Supabase!")
            st.rerun()
          except Exception as err:
            st.error(f"Erro ao guardar projeto: {err}")

    st.markdown("---")
    st.subheader("Projetos Existentes")
    try:
      res = supabase.table("projetos").select("*").execute()
      if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df, use_container_width=True)
      else:
        st.info("Nenhum projeto registado.")
    except Exception:
      st.info("Tabela de projetos vazia ou em configuração.")

  # --- 3. CUSTOS & DESPESAS ---
  elif menu_opcao == "💰 Custos & Despesas":
    st.title("💰 Controlo de Custos & Despesas")
    st.write("Registo de insumos, chapas de MDF, fitas de borda, ferragens e montagem.")

    with st.expander("➕ Registar Nova Despesa / Custo"):
      with st.form("form_despesa"):
        descricao = st.text_input("Descrição do Custo (ex: Chapas MDF Branco TX 15mm)")
        categoria = st.selectbox("Categoria", ["Chapas MDF", "Fita de Borda", "Ferragens", "Mão de Obra / Montagem", "Outros"])
        valor_custo = st.number_input("Valor (R$)", min_value=0.0, step=50.0)
        data_custo = st.date_input("Data")

        btn_custo = st.form_submit_button("Guardar Custo")
        if btn_custo:
          try:
            supabase.table("custos").insert({
                "descricao": descricao,
                "categoria": categoria,
                "valor": valor_custo,
                "data": str(data_custo)
            }).execute()
            st.success("Despesa registada com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao guardar despesa (verifique se a tabela 'custos' existe no Supabase): {e}")

    st.markdown("---")
    st.subheader("Registo de Custos")
    try:
      res_c = supabase.table("custos").select("*").execute()
      if res_c.data:
        st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)
      else:
        st.info("Nenhum custo registado.")
    except Exception:
      st.info("Tabela 'custos' ainda não criada no Supabase.")

  # --- 4. BASE DE CLIENTES ---
  elif menu_opcao == "👥 Base de Clientes":
    st.title("👥 Base de Clientes")
    st.write("Gestão de contactos, moradas e histórico de atendimento.")

    with st.expander("➕ Cadastrar Novo Cliente"):
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
            st.error(f"Erro ao cadastrar cliente (verifique a tabela 'clientes' no Supabase): {e}")

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
    st.write("Gestão de utilizadores, logins de acesso (como sócios/parceiros) e parâmetros.")

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
            st.error(f"Erro ao criar utilizador (verifique se a tabela 'usuarios' existe no Supabase): {e}")

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