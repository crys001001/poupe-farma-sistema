from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests


URL_API = os.getenv(
    "POUPE_FARMA_API_URL",
    "http://100.110.221.91:8000",
).rstrip("/")

TIMEOUT_CONEXAO = 5
TIMEOUT_RESPOSTA = 15


class ErroAPI(Exception):
    """Erro tratado ao comunicar com a API do Poupe Farma."""

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

    def listar_logs_clientes(self, filtro: str = "tudo") -> list[dict[str, Any]]:
        return self._requisicao(
            "GET",
            "/api/clientes/log",
            params={"filtro": filtro},
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

    def listar_historico(self, filtro: str = "tudo") -> list[dict[str, Any]]:
        return self._requisicao(
            "GET",
            "/api/entregas/historico",
            params={"filtro": filtro},
        ) or []
