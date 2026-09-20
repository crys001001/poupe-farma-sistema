import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from backend.servidor import (
    APP_VERSION,
    AfericaoPressao,
    app,
    normalizar_telefone,
    tabela_afericoes_disponivel,
    validar_filtro,
    verificar_saude,
)


class TestBackendValidation(unittest.TestCase):
    def test_release_final_e_rotas_de_afericao_estao_publicadas(self):
        self.assertEqual(APP_VERSION, "1.2.0")
        self.assertEqual(app.version, APP_VERSION)
        rotas = {
            (rota.path, metodo)
            for rota in app.routes
            for metodo in getattr(rota, "methods", set())
        }
        self.assertIn(("/api/saude", "GET"), rotas)
        self.assertIn(("/api/afericoes", "GET"), rotas)
        self.assertIn(("/api/afericoes", "POST"), rotas)

    def test_migration_final_e_idempotente_e_nao_destrutiva(self):
        raiz = Path(__file__).resolve().parent.parent
        sql = (raiz / "database" / "migration_final_1_2_0.sql").read_text(
            encoding="utf-8"
        )
        sql_normalizado = " ".join(sql.upper().split())
        self.assertIn("CREATE TABLE IF NOT EXISTS AFERICOES_PRESSAO", sql_normalizado)
        self.assertNotIn("DROP TABLE", sql_normalizado)
        self.assertNotIn("TRUNCATE TABLE", sql_normalizado)

    def test_healthcheck_confirma_banco_versao_e_afericao(self):
        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def execute(self, sql):
                self._consulta_tabela = "information_schema.tables" in sql

            def fetchone(self):
                return {"total": 1} if self._consulta_tabela else {"ok": 1}

        class Conexao:
            def cursor(self):
                return Cursor()

        @contextmanager
        def banco_falso():
            yield Conexao()

        with patch("backend.servidor.banco", banco_falso):
            resposta = verificar_saude()

        self.assertEqual(resposta["status"], "ok")
        self.assertEqual(resposta["banco"], "conectado")
        self.assertEqual(resposta["versao"], "1.2.0")
        self.assertTrue(resposta["modulos"]["afericao"])

    def test_normaliza_telefone_formatado(self):
        self.assertEqual(normalizar_telefone("(81) 99999-8888", True), "81999998888")

    def test_rejeita_filtro_desconhecido(self):
        with self.assertRaises(Exception) as contexto:
            validar_filtro("ontem")
        self.assertEqual(contexto.exception.status_code, 400)

    def test_rejeita_medidas_fora_da_faixa(self):
        with self.assertRaises(ValidationError):
            AfericaoPressao(sistolica=10, diastolica=80, batimentos=72)

    def test_rejeita_sistolica_menor_que_diastolica(self):
        with self.assertRaises(ValidationError):
            AfericaoPressao(sistolica=70, diastolica=90, batimentos=72)

    def test_aceita_cliente_nao_identificado(self):
        dados = AfericaoPressao(sistolica=120, diastolica=80, batimentos=72)
        self.assertEqual(dados.nome_cliente, "")
        self.assertEqual(dados.telefone, "")

    def test_detecta_tabela_de_afericoes(self):
        class Cursor:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def execute(self, _sql):
                return None

            def fetchone(self):
                return {"total": 1}

        class Conexao:
            def cursor(self):
                return Cursor()

        self.assertTrue(tabela_afericoes_disponivel(Conexao()))


if __name__ == "__main__":
    unittest.main()
