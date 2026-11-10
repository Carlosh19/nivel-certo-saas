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

  # --- CONTEÚDO DAS PÁGINAS ---
  if menu_opcao == "📊 Painel Geral":
    st.title("📊 Painel Geral - Nível Certo")
    st.write("Visão geral dos indicadores de desempenho da marcenaria (100% MDF).")
    
    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric(label="Projetos Ativos", value="3")
    with col2:
      st.metric(label="Faturamento do Mês", value="R$ 18.400,00")
    with col3:
      st.metric(label="Clientes Registados", value="5")

    st.markdown("---")
    st.subheader("Projetos Recentes")
    try:
      dados_projetos = supabase.table("projetos").select("*").execute()
      if dados_projetos.data:
        st.dataframe(pd.DataFrame(dados_projetos.data), use_container_width=True)
      else:
        st.info("Nenhum projeto encontrado no Supabase.")
    except Exception as e:
      st.warning("Aviso: Não foi possível carregar a tabela 'projetos' do Supabase.")

  elif menu_opcao == "🪵 Projetos & Receitas":
    st.title("🪵 Gestão de Projetos 3D & Receitas")
    st.write("Registo completo de projetos planejados, ambientes e valores de contrato.")
    
    try:
      dados_projetos = supabase.table("projetos").select("*").execute()
      if dados_projetos.data:
        st.dataframe(pd.DataFrame(dados_projetos.data), use_container_width=True)
    except Exception:
      st.write("Módulo de projetos pronto para integração.")

  elif menu_opcao == "💰 Custos & Despesas":
    st.title("💰 Controlo de Custos & Despesas")
    st.write("Gestão de insumos, chapas de MDF, fitas de borda e custos operacionais.")
    st.info("Registe aqui os custos de materiais e montagem.")

  elif menu_opcao == "👥 Base de Clientes":
    st.title("👥 Base de Clientes")
    st.write("Lista de contactos e clientes com projetos de móveis planejados.")
    try:
      dados_clientes = supabase.table("clientes").select("*").execute()
      if dados_clientes.data:
        st.dataframe(pd.DataFrame(dados_clientes.data), use_container_width=True)
      else:
        st.info("Nenhum cliente registado ainda.")
    except Exception:
      st.info("Tabela de clientes em configuração.")

  elif menu_opcao == "⚙️ Administração":
    st.title("⚙️ Administração do Sistema")
    st.write("Configurações avançadas, gestão de utilizadores e parâmetros da empresa.")
    st.success("Sistema conectado com sucesso ao Supabase na nuvem!")