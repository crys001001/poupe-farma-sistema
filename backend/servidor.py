from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymysql

app = FastAPI(title="API da Farmácia")

DB_HOST = "coloque o servidor aqui"
DB_USER = "root"
DB_PASSWORD = "coloque sua senha aqui"
DB_NAME = "farmacia"

def conectar_banco():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, cursorclass=pymysql.cursors.DictCursor)

class DadosCliente(BaseModel):
    telefone: str
    nome: str
    endereco: str
    numero: str
    complemento: str

class PedidoEntrega(BaseModel):
    cliente_busca: str 
    conteudo: str

class EdicaoEntrega(BaseModel):
    conteudo: str

# --- CLIENTES ---
@app.post("/api/clientes")
def salvar_cliente(dados: DadosCliente):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    sql = """
        INSERT INTO clientes (telefone, nome, endereco, numero, complemento) 
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE nome=VALUES(nome), endereco=VALUES(endereco), numero=VALUES(numero), complemento=VALUES(complemento)
    """
    cursor.execute(sql, (dados.telefone, dados.nome, dados.endereco, dados.numero, dados.complemento))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Ok"}

@app.get("/api/clientes/{telefone}")
def buscar_cliente(telefone: str):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM clientes WHERE telefone = %s", (telefone,))
    c = cursor.fetchone()
    conexao.close()
    return {"encontrado": bool(c), "dados": c}

@app.get("/api/clientes")
def listar_clientes():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
    res = cursor.fetchall()
    conexao.close()
    return res

@app.delete("/api/clientes/{telefone}")
def deletar_cliente(telefone: str):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM clientes WHERE telefone = %s", (telefone,))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Excluído"}

# --- ENTREGAS ---
@app.post("/api/entregas")
def criar_entrega(dados: PedidoEntrega):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    busca = dados.cliente_busca.strip()
    cursor.execute("SELECT * FROM clientes WHERE telefone = %s OR nome LIKE %s LIMIT 1", (busca, f"%{busca}%"))
    c = cursor.fetchone()
    
    if not c:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
    endereco = f"{c['endereco']}, Nº {c['numero']} - {c['complemento']}"
    sql = "INSERT INTO entregas (nome_cliente, telefone, endereco, conteudo, status) VALUES (%s, %s, %s, %s, 'Pendente')"
    cursor.execute(sql, (c['nome'], c['telefone'], endereco, dados.conteudo))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Ok"}

@app.get("/api/entregas/pendentes")
def listar_pendentes():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM entregas WHERE status = 'Pendente' ORDER BY id ASC")
    res = cursor.fetchall()
    conexao.close()
    return res

@app.put("/api/entregas/{id_entrega}/editar")
def editar_entrega(id_entrega: int, dados: EdicaoEntrega):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("UPDATE entregas SET conteudo = %s WHERE id = %s", (dados.conteudo, id_entrega))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Ok"}

@app.put("/api/entregas/{id_entrega}/{acao}")
def atualizar_status(id_entrega: int, acao: str):
    status = 'Entregue' if acao == 'entregue' else 'Cancelado'
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("UPDATE entregas SET status = %s WHERE id = %s", (status, id_entrega))
    conexao.commit()
    conexao.close()
    return {"mensagem": "Ok"}

@app.get("/api/entregas/historico")
def listar_historico(filtro: str = "tudo"):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    where_clause = "status IN ('Entregue', 'Cancelado')"
    if filtro == "hoje":
        where_clause += " AND DATE(data_criacao) = CURDATE()"
    elif filtro == "7dias":
        where_clause += " AND data_criacao >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
    elif filtro == "30dias":
        where_clause += " AND data_criacao >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        
    
    sql = f"""
        SELECT id, nome_cliente, telefone, endereco, conteudo, status, 
        DATE_FORMAT(data_criacao, '%d/%m/%Y %H:%i') as data_formatada 
        FROM entregas WHERE {where_clause} ORDER BY id DESC LIMIT 100
    """
    
    try:
        cursor.execute(sql)
    except:
        
        cursor.execute("SELECT *, 'Sem Data' as data_formatada FROM entregas WHERE status IN ('Entregue', 'Cancelado') ORDER BY id DESC LIMIT 100")
        
    res = cursor.fetchall()
    conexao.close()
    return res