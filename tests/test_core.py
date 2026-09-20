import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from models.api_model import (
    ERRO_MODULO_AFERICAO,
    ErroAPI,
    FarmaciaAPI,
    carregar_url_api,
)
from models.impressora_model import ImpressoraTermica
from view.config import formatar_endereco, formatar_telefone, texto_opcional


class TestFormatacao(unittest.TestCase):
    def test_formata_telefone_celular(self):
        self.assertEqual(formatar_telefone("81999998888"), "(81) 99999-8888")

    def test_endereco_totalmente_opcional(self):
        self.assertEqual(formatar_endereco({}), "Endereço não informado")

    def test_endereco_parcial_nao_gera_separadores_soltos(self):
        self.assertEqual(
            formatar_endereco({"endereco": "Rua A", "bairro": "Centro"}),
            "Rua A - Centro",
        )

    def test_texto_opcional_rejeita_pontuacao_vazia(self):
        self.assertEqual(texto_opcional(" - , . "), "Não informado")


class TestClienteAPI(unittest.TestCase):
    @patch.dict(os.environ, {"POUPE_FARMA_API_URL": "http://api.local:9000/"})
    def test_url_da_api_pode_ser_configurada_por_ambiente(self):
        self.assertEqual(carregar_url_api(), "http://api.local:9000")

    @patch.dict(os.environ, {}, clear=True)
    @patch("models.api_model.pasta_aplicacao")
    def test_url_da_api_pode_ser_configurada_ao_lado_do_exe(self, pasta):
        with tempfile.TemporaryDirectory() as temporaria:
            raiz = Path(temporaria)
            (raiz / "config.ini").write_text(
                "[api]\nurl = http://servidor-tailscale:8000/\n",
                encoding="utf-8",
            )
            pasta.return_value = raiz
            self.assertEqual(
                carregar_url_api(),
                "http://servidor-tailscale:8000",
            )

    @patch("models.api_model.requests.request")
    def test_exportacao_solicita_limite_completo(self, request):
        resposta = Mock(ok=True, content=b"[]")
        resposta.json.return_value = []
        request.return_value = resposta

        FarmaciaAPI("http://servidor").listar_historico("30dias", limite=5000)

        self.assertEqual(
            request.call_args.kwargs["params"],
            {"filtro": "30dias", "limite": 5000},
        )

    def test_extrai_mensagem_de_validacao_do_fastapi(self):
        resposta = Mock(status_code=422)
        resposta.json.return_value = {
            "detail": [
                {"loc": ["body", "nome"], "msg": "Field required"},
                {"loc": ["body", "telefone"], "msg": "Value error, telefone inválido"},
            ]
        }

        mensagem = FarmaciaAPI._extrair_erro(resposta)

        self.assertIn("Field required", mensagem)
        self.assertIn("telefone inválido", mensagem)

    @patch("models.api_model.requests.request")
    def test_traduz_404_da_afericao_em_instrucao_util(self, request):
        resposta = Mock(ok=False, content=b'{"detail":"Not Found"}', status_code=404)
        resposta.json.return_value = {"detail": "Not Found"}
        request.return_value = resposta

        with self.assertRaises(ErroAPI) as contexto:
            FarmaciaAPI("http://servidor").listar_afericoes()

        self.assertEqual(contexto.exception.status_code, 404)
        self.assertEqual(str(contexto.exception), ERRO_MODULO_AFERICAO)


class TestComprovante(unittest.TestCase):
    def test_comprovante_tem_inicializacao_corte_e_acentos_cp850(self):
        dados = {
            "nome_cliente": "José",
            "telefone": "81999998888",
            "sistolica": 120,
            "diastolica": 80,
            "batimentos": 72,
            "valor": "5.00",
            "data_formatada": "04/09/2026 09:30",
        }

        comprovante = ImpressoraTermica.montar_comprovante(dados)

        self.assertTrue(comprovante.startswith(b"\x1b@"))
        self.assertIn("AFERIÇÃO".encode("cp850"), comprovante)
        self.assertIn(b"120 / 80 mmHg", comprovante)
        self.assertTrue(comprovante.endswith(b"\x1dV\x00"))


if __name__ == "__main__":
    unittest.main()
