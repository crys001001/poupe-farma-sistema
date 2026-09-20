from contextlib import contextmanager
from pathlib import Path
import logging
import os

import pymysql
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, model_validator


# Carrega o .env localizado na mesma pasta deste arquivo.
load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("sistema_cadastro")

APP_VERSION = "1.2.0"

app = FastAPI(
    title="API da Farmácia",
    version=APP_VERSION,
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
    telefone: str = Field(max_length=20)
    nome: str = Field(max_length=100)
    endereco: str = Field(default="", max_length=200)
    numero: str = Field(default="", max_length=20)
    bairro: str = Field(default="", max_length=100)
    complemento: str = Field(default="", max_length=150)
    produto_desejo: str = Field(default="", max_length=255)


class PedidoEntrega(BaseModel):
    cliente_busca: str = Field(max_length=100)
    conteudo: str = Field(max_length=4000)


class EdicaoEntrega(BaseModel):
    conteudo: str = Field(max_length=4000)


class AfericaoPressao(BaseModel):
    nome_cliente: str = Field(default="", max_length=100)
    telefone: str = Field(default="", max_length=20)
    sistolica: int = Field(ge=30, le=300)
    diastolica: int = Field(ge=20, le=200)
    batimentos: int = Field(ge=20, le=300)

    @model_validator(mode="after")
    def validar_ordem_pressao(self):
        if self.sistolica < self.diastolica:
            raise ValueError(
                "A pressão sistólica não pode ser menor que a diastólica."
            )
        return self


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


def normalizar_telefone(valor: str, obrigatorio: bool = False) -> str:
    numero = "".join(filter(str.isdigit, str(valor or "")))

    if not numero and not obrigatorio:
        return ""

    if len(numero) not in (10, 11):
        raise HTTPException(
            status_code=422,
            detail="Informe um telefone válido com DDD.",
        )

    return numero


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


def tabela_afericoes_disponivel(conexao) -> bool:
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
              AND table_name = 'afericoes_pressao'
            """
        )
        resultado = cursor.fetchone() or {}
    return bool(resultado.get("total"))


def exigir_tabela_afericoes(conexao):
    if not tabela_afericoes_disponivel(conexao):
        raise HTTPException(
            status_code=503,
            detail=(
                "Módulo de aferição indisponível no servidor. "
                "Aplique a migration da tabela afericoes_pressao."
            ),
        )

# =============================================================================
# SAÚDE DA API
# =============================================================================


@app.get("/")
def inicio():
    return {
        "sistema": "Sistema de Cadastro",
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

        tabela_afericoes = tabela_afericoes_disponivel(conexao)

    return {
        "status": "ok",
        "banco": "conectado",
        "versao": app.version,
        "modulos": {
            "afericao": tabela_afericoes,
        },
    }


# =============================================================================
# CLIENTES
# =============================================================================


@app.post("/api/clientes")
def salvar_cliente(dados: DadosCliente):
    telefone = normalizar_telefone(dados.telefone, obrigatorio=True)

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
    limite: int = Query(default=100, ge=1, le=5000),
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
                '%%d/%%m/%%Y %%H:%%i'
            ) AS data_formatada
        FROM clientes
        WHERE {where_clause}
        ORDER BY data_cadastro DESC
        LIMIT %s
    """

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql, (limite,))

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
    telefone = normalizar_telefone(telefone, obrigatorio=True)

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
    telefone = normalizar_telefone(telefone, obrigatorio=True)

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
# AFERIÇÕES DE PRESSÃO
# =============================================================================


@app.post("/api/afericoes")
def registrar_afericao(dados: AfericaoPressao):
    nome = dados.nome_cliente.strip()
    telefone = normalizar_telefone(dados.telefone)

    with banco() as conexao:
        exigir_tabela_afericoes(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO afericoes_pressao
                (nome_cliente, telefone, sistolica, diastolica, batimentos, valor)
                VALUES (%s, %s, %s, %s, %s, 5.00)
                """,
                (nome, telefone, dados.sistolica, dados.diastolica, dados.batimentos),
            )
            id_afericao = cursor.lastrowid

            cursor.execute(
                """
                SELECT
                    id, nome_cliente, telefone, sistolica, diastolica,
                    batimentos, valor,
                    DATE_FORMAT(
                        DATE_SUB(data_criacao, INTERVAL 3 HOUR),
                        '%%d/%%m/%%Y %%H:%%i'
                    ) AS data_formatada
                FROM afericoes_pressao
                WHERE id = %s
                """,
                (id_afericao,),
            )
            registro = cursor.fetchone()

        conexao.commit()

    return registro


@app.get("/api/afericoes")
def listar_afericoes(filtro: str = "hoje"):
    filtro = validar_filtro(filtro)
    where_clause = "1=1" + periodo_sql("data_criacao", filtro)
    sql = f"""
        SELECT
            id, nome_cliente, telefone, sistolica, diastolica,
            batimentos, valor,
            DATE_FORMAT(
                DATE_SUB(data_criacao, INTERVAL 3 HOUR),
                '%d/%m/%Y %H:%i'
            ) AS data_formatada
        FROM afericoes_pressao
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT 200
    """

    with banco() as conexao:
        exigir_tabela_afericoes(conexao)
        with conexao.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


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
            busca_digitos = "".join(filter(str.isdigit, busca))
            telefone_busca = busca_digitos if len(busca_digitos) in (10, 11) else busca

            cursor.execute(
                """
                SELECT *
                FROM clientes
                WHERE telefone = %s OR nome LIKE %s
                ORDER BY
                    CASE WHEN telefone = %s THEN 0 ELSE 1 END,
                    nome ASC
                LIMIT 3
                """,
                (telefone_busca, f"%{busca}%", telefone_busca),
            )
            encontrados = cursor.fetchall()

            if not encontrados:
                raise HTTPException(status_code=404, detail="Cliente não encontrado.")

            exato_telefone = next(
                (item for item in encontrados if item["telefone"] == telefone_busca),
                None,
            )
            if exato_telefone:
                cliente = exato_telefone
            else:
                exatos_nome = [
                    item for item in encontrados
                    if str(item["nome"]).strip().casefold() == busca.casefold()
                ]
                if len(exatos_nome) == 1:
                    cliente = exatos_nome[0]
                elif len(encontrados) > 1:
                    raise HTTPException(
                        status_code=409,
                        detail=(
                            "Mais de um cliente corresponde à busca. "
                            "Informe o telefone para escolher o cliente correto."
                        ),
                    )
                else:
                    cliente = encontrados[0]

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
                SELECT
                    id,
                    nome_cliente,
                    telefone,
                    endereco,
                    conteudo,
                    status,
                    DATE_FORMAT(
                        DATE_SUB(data_criacao, INTERVAL 3 HOUR),
                        '%d/%m/%Y %H:%i'
                    ) AS data_formatada
                FROM entregas
                WHERE status = 'Pendente'
                ORDER BY id ASC
                """
            )

            return cursor.fetchall()


@app.get("/api/entregas/historico")
def listar_historico(
    filtro: str = "tudo",
    limite: int = Query(default=100, ge=1, le=5000),
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
                '%%d/%%m/%%Y %%H:%%i'
            ) AS data_formatada
        FROM entregas
        WHERE {where_clause}
        ORDER BY id DESC
        LIMIT %s
    """

    with banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql, (limite,))

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
