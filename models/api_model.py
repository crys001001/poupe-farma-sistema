from __future__ import annotations

from configparser import ConfigParser
import os
from pathlib import Path
import sys
from typing import Any
from urllib.parse import quote

import requests


URL_API_PADRAO = "http://127.0.0.1:8000"


def pasta_aplicacao() -> Path:
    """Pasta editável ao lado do EXE ou raiz do projeto em desenvolvimento."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def carregar_url_api() -> str:
    """Lê a URL pela variável de ambiente ou pelo config.ini do aplicativo."""
    url_ambiente = os.getenv("POUPE_FARMA_API_URL", "").strip()
    if url_ambiente:
        return url_ambiente.rstrip("/")

    arquivo = pasta_aplicacao() / "config.ini"
    parser = ConfigParser(interpolation=None)
    try:
        parser.read(arquivo, encoding="utf-8")
        url_configurada = parser.get("api", "url", fallback="").strip()
    except (OSError, ValueError):
        url_configurada = ""

    return (url_configurada or URL_API_PADRAO).rstrip("/")


URL_API = carregar_url_api()

TIMEOUT_CONEXAO = 5
TIMEOUT_RESPOSTA = 15

ERRO_MODULO_AFERICAO = (
    "Módulo de aferição indisponível no servidor. "
    "Atualize a API e aplique a migration da tabela afericoes_pressao."
)


class ErroAPI(Exception):
    """Erro tratado ao comunicar com a API do Sistema de Cadastro."""

    def __init__(self, mensagem: str, status_code: int | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


class FarmaciaAPI:
    def __init__(self, url_api: str = URL_API):
        self.url_api = url_api.rstrip("/")

    def _requisicao(
        self,
        metodo: str,
        rota: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.url_api}{rota}"

        try:
            resposta = requests.request(
                method=metodo,
                url=url,
                json=json,
                params=params,
                timeout=(TIMEOUT_CONEXAO, TIMEOUT_RESPOSTA),
            )
        except requests.exceptions.ConnectTimeout as erro:
            raise ErroAPI("Não foi possível conectar ao servidor.") from erro
        except requests.exceptions.ReadTimeout as erro:
            raise ErroAPI("O servidor demorou demais para responder.") from erro
        except requests.exceptions.ConnectionError as erro:
            raise ErroAPI(
                "Servidor indisponível. Verifique a internet e o Tailscale."
            ) from erro
        except requests.exceptions.RequestException as erro:
            raise ErroAPI(
                "Erro inesperado na comunicação com o servidor."
            ) from erro

        if not resposta.ok:
            raise ErroAPI(
                self._extrair_erro(resposta),
                resposta.status_code,
            )

        if not resposta.content:
            return None

        try:
            return resposta.json()
        except ValueError as erro:
            raise ErroAPI("O servidor enviou uma resposta inválida.") from erro

    @staticmethod
    def _extrair_erro(resposta: requests.Response) -> str:
        try:
            dados = resposta.json()
        except ValueError:
            return f"Erro HTTP {resposta.status_code} retornado pelo servidor."

        if isinstance(dados, dict):
            detalhe = dados.get("detail")
            if isinstance(detalhe, str):
                return detalhe
            if isinstance(detalhe, list):
                mensagens = []
                for item in detalhe:
                    if not isinstance(item, dict):
                        continue
                    mensagem = str(item.get("msg") or "").strip()
                    if mensagem.lower().startswith("value error,"):
                        mensagem = mensagem.split(",", 1)[1].strip()
                    if mensagem and mensagem not in mensagens:
                        mensagens.append(mensagem)
                if mensagens:
                    return "Dados inválidos: " + "; ".join(mensagens) + "."

            mensagem = dados.get("mensagem")
            if isinstance(mensagem, str):
                return mensagem

        return f"Erro HTTP {resposta.status_code} retornado pelo servidor."

    def verificar_saude(self) -> dict[str, Any]:
        resultado = self._requisicao("GET", "/api/saude")
        return resultado or {}

    def buscar_cliente(self, telefone: str) -> dict[str, Any]:
        telefone_seguro = quote(telefone.strip(), safe="")
        resultado = self._requisicao(
            "GET",
            f"/api/clientes/{telefone_seguro}",
        )
        return resultado or {"encontrado": False, "dados": None}

    def salvar_cliente(self, dados: dict[str, Any]) -> bool:
        self._requisicao("POST", "/api/clientes", json=dados)
        return True

    def listar_clientes(self) -> list[dict[str, Any]]:
        return self._requisicao("GET", "/api/clientes") or []

    def listar_logs_clientes(
        self,
        filtro: str = "tudo",
        limite: int = 100,
    ) -> list[dict[str, Any]]:
        return self._requisicao(
            "GET",
            "/api/clientes/log",
            params={"filtro": filtro, "limite": limite},
        ) or []

    def excluir_cliente(self, telefone: str) -> bool:
        telefone_seguro = quote(telefone.strip(), safe="")
        self._requisicao("DELETE", f"/api/clientes/{telefone_seguro}")
        return True

    def lancar_entrega(self, cliente_busca: str, conteudo: str) -> bool:
        self._requisicao(
            "POST",
            "/api/entregas",
            json={"cliente_busca": cliente_busca, "conteudo": conteudo},
        )
        return True

    def listar_pendentes(self) -> list[dict[str, Any]]:
        return self._requisicao("GET", "/api/entregas/pendentes") or []

    def editar_conteudo_entrega(
        self,
        id_entrega: int,
        novo_conteudo: str,
    ) -> bool:
        self._requisicao(
            "PUT",
            f"/api/entregas/{id_entrega}/editar",
            json={"conteudo": novo_conteudo},
        )
        return True

    def alterar_status_entrega(self, id_entrega: int, acao: str) -> bool:
        acao = acao.strip().lower()
        if acao not in {"entregue", "cancelado"}:
            raise ErroAPI("Ação inválida para a entrega.")

        self._requisicao(
            "PUT",
            f"/api/entregas/{id_entrega}/{acao}",
        )
        return True

    def listar_historico(
        self,
        filtro: str = "tudo",
        limite: int = 100,
    ) -> list[dict[str, Any]]:
        return self._requisicao(
            "GET",
            "/api/entregas/historico",
            params={"filtro": filtro, "limite": limite},
        ) or []

    def registrar_afericao(self, dados: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._requisicao(
                "POST",
                "/api/afericoes",
                json=dados,
            ) or {}
        except ErroAPI as erro:
            if erro.status_code == 404:
                raise ErroAPI(ERRO_MODULO_AFERICAO, 404) from erro
            raise

    def listar_afericoes(self, filtro: str = "hoje") -> list[dict[str, Any]]:
        try:
            return self._requisicao(
                "GET",
                "/api/afericoes",
                params={"filtro": filtro},
            ) or []
        except ErroAPI as erro:
            if erro.status_code == 404:
                raise ErroAPI(ERRO_MODULO_AFERICAO, 404) from erro
            raise
