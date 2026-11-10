import pandas as pd
import streamlit as st
from supabase import create_client

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gestão Nível Certo", page_icon="🪵", layout="wide"
)

# Configuração das credenciais do Supabase
SUPABASE_URL = "https://hzpmzxtpozifbkzjffkq.supabase.co"
SUPABASE_KEY = "sb_publishable_Nguzd6BG38Ztw4MjhjRZlg_K31XGf1X"

# Inicialização do cliente Supabase
@st.cache_resource
def init_supabase():
  return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- TELA DE LOGIN ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("Gestão Nível Certo")
  st.subheader("Faça login para aceder ao painel")

  email_input = st.text_input("E-mail", value="carlos.diference@gmail.com")
  senha_input = st.text_input("Palavra-passe", type="password")

  if st.button("Entrar"):
    # Validação direta ou consulta rápida no Supabase
    if email_input == "carlos.diference@gmail.com" and senha_input == "teste123456":
      st.session_state.autenticado = True
      st.session_state.usuario = {"nome": "Carlos", "email": email_input}
      st.rerun()
    else:
      try:
        # Exemplo de consulta à tabela de utilizadores no Supabase caso exista
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
      except Exception as e:
        st.error("E-mail ou palavra-passe incorretos.")

else:
  # --- PAINEL PRINCIPAL APÓS O LOGIN ---
  st.sidebar.title("Menu Nível Certo")
  if st.sidebar.button("Terminar Sessão"):
    st.session_state.autenticado = False
    st.rerun()

  st.title("Painel de Controlo - Projetos 3D e Móveis Planejados")
  st.write(
      "Bem-vindo ao sistema de gestão integrado. Todos os módulos operam"
      " diretamente na nuvem com 100% MDF."
  )

  tab1, tab2 = st.tabs(["Projetos", "Financeiro"])

  with tab1:
    st.header("Gestão de Projetos 3D")
    st.info("Aqui serão listados os projetos em curso a partir do Supabase.")
    
    # Exemplo de como buscar dados de uma tabela do Supabase (ex: 'projetos')
    try:
      dados_projetos = supabase.table("projetos").select("*").execute()
      if dados_projetos.data:
        df_projetos = pd.DataFrame(dados_projetos.data)
        st.dataframe(df_projetos, use_container_width=True)
      else:
        st.write("Ainda não existem projetos registados na base de dados.")
    except Exception as e:
      st.write("A tabela 'projetos' será exibida aqui assim que configurada.")

  with tab2:
    st.header("Resumo Financeiro")
    st.metric(label="Faturamento Mensal", value="R$ 0,00")