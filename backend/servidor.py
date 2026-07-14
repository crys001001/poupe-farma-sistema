from contextlib import contextmanager
from pathlib import Path
import logging
import os

import pymysql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Carrega o .env localizado na mesma pasta deste arquivo.
load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("poupe_farma")

app = FastAPI(
    title="API da Farmácia",
    version="0.9.1",
)


# =============================================================================
# BANCO DE DADOS
# =============================================================================


def conectar_banco():
    configuracao = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    faltando = [
        nome
        for nome, valor in configuracao.items()
        if not valor
    ]

    if faltando:
        raise RuntimeError(
            "Configuração do banco incompleta: "
            + ", ".join(faltando)
        )

    return pymysql.connect(
        **configuracao,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=False,
    )


@contextmanager
def banco():
    conexao = None

    try:
        conexao = conectar_banco()
        yield conexao

    except HTTPException:
        if conexao:
            conexao.rollback()

        raise

    except Exception:
        if conexao:
            conexao.rollback()

        logger.exception(
            "Erro interno de banco de dados"
        )

        raise HTTPException(
            status_code=500,
            detail="Erro interno no servidor.",
        )

    finally:
        if conexao:
            conexao.close()


# =============================================================================
# MODELOS
# =============================================================================


class DadosCliente(BaseModel):
    telefone: str
    nome: str
    endereco: str = ""
    numero: str = ""
    bairro: str = ""
    complemento: str = ""
    produto_desejo: str = ""


class PedidoEntrega(BaseModel):
    cliente_busca: str
    conteudo: str


class EdicaoEntrega(BaseModel):
    conteudo: str


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================


def texto_obrigatorio(
    valor: str,
    campo: str,
) -> str:
    valor = valor.strip()

    if not valor:
        raise HTTPException(
            status_code=422,
            detail=f"O campo '{campo}' é obrigatório.",
        )

    return valor


def validar_filtro(filtro: str) -> str:
    filtro = filtro.strip().lower()

    filtros_validos = {
        "tudo",
        "hoje",
        "7dias",
        "30dias",
    }

    if filtro not in filtros_validos:
        raise HTTPException(
            status_code=400,
            detail=(
                "Filtro inválido. "
                "Use: tudo, hoje, 7dias ou 30dias."
            ),
        )

    return filtro


def periodo_sql(coluna: str, filtro: str) -> str:
    """
    Converte tanto a data do registro quanto a data atual
    de UTC para o horário de Pernambuco (UTC-3).
    """

    coluna_local = (
        f"DATE_SUB({coluna}, INTERVAL 3 HOUR)"
    )

    hoje_local = (
        "DATE(DATE_SUB(UTC_TIMESTAMP(), INTERVAL 3 HOUR))"
    )

    if filtro == "hoje":
        return (
            f" AND DATE({coluna_local}) = {hoje_local}"
        )

    if filtro == "7dias":
        return (
            f" AND {coluna_local} "
            f">= DATE_SUB({hoje_local}, INTERVAL 6 DAY)"
            f" AND {coluna_local} "
            f"< DATE_ADD({hoje_local}, INTERVAL 1 DAY)"
        )

    if filtro == "30dias":
        return (
            f" AND {coluna_local} "
            f">= DATE_SUB({hoje_local}, INTERVAL 29 DAY)"
            f" AND {coluna_local} "
            f"< DATE_ADD({hoje_local}, INTERVAL 1 DAY)"
        )

    return ""

# =============================================================================
# SAÚDE DA API
# =============================================================================


@app.get("/")
def inicio():
    return {
        "sistema": "Poupe Farma",
        "status": "online",
        "versao": app.version,
    }


@app.get("/api/saude")
def verificar_saude():
    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT 1 AS ok"
            )

            cursor.fetchone()

    return {
        "status": "ok",
        "banco": "conectado",
        "versao": app.version,
    }


# =============================================================================
# CLIENTES
# =============================================================================


@app.post("/api/clientes")
def salvar_cliente(dados: DadosCliente):
    telefone = texto_obrigatorio(
        dados.telefone,
        "telefone",
    )

    nome = texto_obrigatorio(
        dados.nome,
        "nome",
    )

    endereco = dados.endereco.strip()
    numero = dados.numero.strip()

    sql = """
        INSERT INTO clientes
        (
            telefone,
            nome,
            endereco,
            numero,
            bairro,
            complemento,
            produto_desejo
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON DUPLICATE KEY UPDATE
            nome = VALUES(nome),
            endereco = VALUES(endereco),
            numero = VALUES(numero),
            bairro = VALUES(bairro),
            complemento = VALUES(complemento),
            produto_desejo = VALUES(produto_desejo)
    """

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    telefone,
                    nome,
                    endereco,
                    numero,
                    dados.bairro.strip(),
                    dados.complemento.strip(),
                    dados.produto_desejo.strip(),
                ),
            )

        conexao.commit()

    return {
        "mensagem": "Ok"
    }


# Esta rota precisa ficar antes de
# /api/clientes/{telefone}.
@app.get("/api/clientes/log")
def log_cadastros(
    filtro: str = "tudo",
):
    filtro = validar_filtro(filtro)

    where_clause = (
        "1=1"
        + periodo_sql(
            "data_cadastro",
            filtro,
        )
    )

    sql = f"""
        SELECT
            *,
            DATE_FORMAT(
                DATE_SUB(
                    data_cadastro,
                    INTERVAL 3 HOUR
                ),
                '%d/%m/%Y %H:%i'
            ) AS data_formatada
        FROM clientes
        WHERE {where_clause}
        ORDER BY data_cadastro DESC
        LIMIT 100
    """

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql)

            return cursor.fetchall()


@app.get("/api/clientes")
def listar_clientes():
    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM clientes
                ORDER BY nome ASC
                """
            )

            return cursor.fetchall()


@app.get("/api/clientes/{telefone}")
def buscar_cliente(
    telefone: str,
):
    telefone = texto_obrigatorio(
        telefone,
        "telefone",
    )

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM clientes
                WHERE telefone = %s
                """,
                (telefone,),
            )

            cliente = cursor.fetchone()

    return {
        "encontrado": bool(cliente),
        "dados": cliente,
    }


@app.delete("/api/clientes/{telefone}")
def deletar_cliente(
    telefone: str,
):
    telefone = texto_obrigatorio(
        telefone,
        "telefone",
    )

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM clientes
                WHERE telefone = %s
                """,
                (telefone,),
            )

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente não encontrado.",
                )

        conexao.commit()

    return {
        "mensagem": "Excluído"
    }


# =============================================================================
# ENTREGAS
# =============================================================================


@app.post("/api/entregas")
def criar_entrega(
    dados: PedidoEntrega,
):
    busca = texto_obrigatorio(
        dados.cliente_busca,
        "cliente_busca",
    )

    conteudo = texto_obrigatorio(
        dados.conteudo,
        "conteudo",
    )

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM clientes
                WHERE
                    telefone = %s
                    OR nome LIKE %s
                ORDER BY
                    CASE
                        WHEN telefone = %s
                        THEN 0
                        ELSE 1
                    END,
                    nome ASC
                LIMIT 1
                """,
                (
                    busca,
                    f"%{busca}%",
                    busca,
                ),
            )

            cliente = cursor.fetchone()

            if not cliente:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente não encontrado.",
                )

            partes_endereco = []

            endereco_base = str(
                cliente.get("endereco") or ""
            ).strip()

            numero = str(
                cliente.get("numero") or ""
            ).strip()

            bairro = str(
                cliente.get("bairro") or ""
            ).strip()

            complemento = str(
                cliente.get("complemento") or ""
            ).strip()

            if endereco_base:
                partes_endereco.append(endereco_base)

            if numero:
                partes_endereco.append(f"Nº {numero}")

            if bairro:
                partes_endereco.append(bairro)

            if complemento:
                partes_endereco.append(complemento)

            endereco = (
                " - ".join(partes_endereco)
                if partes_endereco
                else "Endereço não informado"
            )

            cursor.execute(
                """
                INSERT INTO entregas
                (
                    nome_cliente,
                    telefone,
                    endereco,
                    conteudo,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    'Pendente'
                )
                """,
                (
                    cliente["nome"],
                    cliente["telefone"],
                    endereco,
                    conteudo,
                ),
            )

        conexao.commit()

    return {
        "mensagem": "Ok"
    }


@app.get("/api/entregas/pendentes")
def listar_pendentes():
    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM entregas
                WHERE status = 'Pendente'
                ORDER BY id ASC
                """
            )

            return cursor.fetchall()


@app.get("/api/entregas/historico")
def listar_historico(
    filtro: str = "tudo",
):
    filtro = validar_filtro(filtro)

    where_clause = (
        "status IN ('Entregue', 'Cancelado')"
        + periodo_sql(
            "data_criacao",
            filtro,
        )
    )

    sql = f"""
        SELECT
            id,
            nome_cliente,
            telefone,
            endereco,
            conteudo,
            status,
            DATE_FORMAT(
                DATE_SUB(
                    data_criacao,
                    INTERVAL 3 HOUR
                ),
                '%d/%m/%Y %H:%i'
            ) AS data_formatada
        FROM entregas
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT 100
    """

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql)

            return cursor.fetchall()


# Esta rota precisa ficar antes da rota genérica {acao}.
@app.put("/api/entregas/{id_entrega}/editar")
def editar_entrega(
    id_entrega: int,
    dados: EdicaoEntrega,
):
    conteudo = texto_obrigatorio(
        dados.conteudo,
        "conteudo",
    )

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    status
                FROM entregas
                WHERE id = %s
                """,
                (id_entrega,),
            )

            entrega = cursor.fetchone()

            if not entrega:
                raise HTTPException(
                    status_code=404,
                    detail="Entrega não encontrada.",
                )

            if entrega["status"] != "Pendente":
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Uma entrega finalizada "
                        "não pode ser editada."
                    ),
                )

            cursor.execute(
                """
                UPDATE entregas
                SET conteudo = %s
                WHERE id = %s
                """,
                (
                    conteudo,
                    id_entrega,
                ),
            )

        conexao.commit()

    return {
        "mensagem": "Ok"
    }


@app.put("/api/entregas/{id_entrega}/{acao}")
def atualizar_status(
    id_entrega: int,
    acao: str,
):
    acoes_validas = {
        "entregue": "Entregue",
        "cancelado": "Cancelado",
    }

    acao = acao.strip().lower()

    if acao not in acoes_validas:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ação inválida. "
                "Use 'entregue' ou 'cancelado'."
            ),
        )

    status = acoes_validas[acao]

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    status
                FROM entregas
                WHERE id = %s
                """,
                (id_entrega,),
            )

            entrega = cursor.fetchone()

            if not entrega:
                raise HTTPException(
                    status_code=404,
                    detail="Entrega não encontrada.",
                )

            if entrega["status"] != "Pendente":
                raise HTTPException(
                    status_code=409,
                    detail="A entrega já foi finalizada.",
                )

            cursor.execute(
                """
                UPDATE entregas
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    id_entrega,
                ),
            )

        conexao.commit()

    return {
        "mensagem": "Ok",
        "status": status,
    }
