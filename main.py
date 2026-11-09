from fastapi import FastAPI
import uvicorn
from supabase import create_client
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

SUPABASE_URL = "https://hzpmzxtpozifbkzjffkq.supabase.co"
SUPABASE_KEY = "sb_publishable_Nguzd6BG38Ztw4MjhjRZlg_K31XGf1X"
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ClienteModel(BaseModel):
    nome: str
    email: Optional[str] = ""
    telefone: Optional[str] = ""
    endereco: Optional[str] = ""

class ProjetoModel(BaseModel):
    id_projeto_txt: str
    cliente_nome: str
    ambiente: str
    data_inicio: str
    valor_contrato: float
    valor_recebido: float
    status_projeto: str
    status_pagamento: str

class DespesaModel(BaseModel):
    data_lancamento: str
    mao_de_obra: float
    descricao: str
    forma_pagamento: str
    valor_total: float
    status_pagamento: str
    projeto_vinculado: Optional[str] = ""

@app.get("/")
def principal():
    return {"mensagem": "API no ar!"}

# --- ROTAS CLIENTES ---
@app.post("/clientes")
def cadastrar_cliente(cliente: ClienteModel):
    try: return supabase_client.table("clientes").insert(cliente.model_dump()).execute().data
    except Exception as e: return {"erro": str(e)}

@app.get("/clientes")
def listar_clientes():
    return supabase_client.table("clientes").select("*").execute().data

@app.put("/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, cliente: ClienteModel):
    try: return supabase_client.table("clientes").update(cliente.model_dump()).eq("id", cliente_id).execute().data
    except Exception as e: return {"erro": str(e)}

@app.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int):
    try: return supabase_client.table("clientes").delete().eq("id", cliente_id).execute().data
    except Exception as e: return {"erro": str(e)}

# --- ROTAS PROJETOS ---
@app.post("/projetos")
def cadastrar_projeto(projeto: ProjetoModel):
    try: return supabase_client.table("projetos").insert(projeto.model_dump()).execute().data
    except Exception as e: return {"erro": str(e)}

@app.get("/projetos")
def listar_projetos():
    return supabase_client.table("projetos").select("*").execute().data

@app.put("/projetos/{id_projeto_txt}")
def atualizar_projeto(id_projeto_txt: str, projeto: ProjetoModel):
    try: return supabase_client.table("projetos").update(projeto.model_dump()).eq("id_projeto_txt", id_projeto_txt).execute().data
    except Exception as e: return {"erro": str(e)}

@app.delete("/projetos/{id_projeto_txt}")
def deletar_projeto(id_projeto_txt: str):
    try: return supabase_client.table("projetos").delete().eq("id_projeto_txt", id_projeto_txt).execute().data
    except Exception as e: return {"erro": str(e)}

# --- ROTAS DESPESAS ---
@app.post("/despesas")
def cadastrar_despesa(despesa: DespesaModel):
    try: return supabase_client.table("despesas").insert(despesa.model_dump()).execute().data
    except Exception as e: return {"erro": str(e)}

@app.get("/despesas")
def listar_despesas():
    return supabase_client.table("despesas").select("*").execute().data

@app.delete("/despesas/{desp_id}")
def deletar_despesa(desp_id: int):
    try: return supabase_client.table("despesas").delete().eq("id", desp_id).execute().data
    except Exception as e: return {"erro": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)