from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


class ErroImpressao(Exception):
    pass


class ImpressoraTermica:
    """Impressão ESC/POS pelo spooler do Windows."""

    CONFIG = Path.home() / "SistemaCadastro" / "config.json"

    @staticmethod
    def _win32print():
        try:
            import win32print
        except ImportError as erro:
            raise ErroImpressao(
                "Suporte de impressão ausente. Instale o pywin32 e gere o executável novamente."
            ) from erro
        return win32print

    def listar(self) -> list[str]:
        win32print = self._win32print()
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        return sorted({item[2] for item in win32print.EnumPrinters(flags)})

    def padrao(self) -> str | None:
        try:
            return self._win32print().GetDefaultPrinter()
        except Exception:
            return None

    def preferida(self) -> str | None:
        try:
            return json.loads(self.CONFIG.read_text(encoding="utf-8")).get("impressora")
        except Exception:
            return None

    def salvar_preferida(self, nome: str):
        try:
            self.CONFIG.parent.mkdir(parents=True, exist_ok=True)
            self.CONFIG.write_text(
                json.dumps({"impressora": nome}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    @staticmethod
    def _valor_monetario(valor: Any) -> str:
        try:
            numero = Decimal(str(valor))
        except Exception:
            numero = Decimal("5.00")
        return f"R$ {numero:.2f}".replace(".", ",")

    @classmethod
    def montar_comprovante(cls, dados: dict[str, Any]) -> bytes:
        nome = str(dados.get("nome_cliente") or "").strip()
        telefone = str(dados.get("telefone") or "").strip()
        data = str(dados.get("data_formatada") or "").strip() or datetime.now().strftime("%d/%m/%Y %H:%M")

        linhas = ["-" * 42, f"Data: {data}"]
        if nome:
            linhas.append(f"Cliente: {nome}")
        if telefone:
            linhas.append(f"Telefone: {telefone}")
        linhas += [
            "-" * 42,
            "PRESSÃO ARTERIAL",
            f"{dados.get('sistolica', '')} / {dados.get('diastolica', '')} mmHg",
            "",
            "BATIMENTOS CARDÍACOS",
            f"{dados.get('batimentos', '')} bpm",
            "",
            f"Valor do serviço: {cls._valor_monetario(dados.get('valor', 5))}",
            "-" * 42,
            "Comprovante dos valores aferidos.",
            "Não substitui avaliação médica.",
            "-" * 42,
        ]

        titulo = "SISTEMA DE CADASTRO\nAFERIÇÃO DE PRESSÃO\n".encode(
            "cp850", errors="replace"
        )
        corpo = "\n".join(linhas).encode("cp850", errors="replace")
        return (
            b"\x1b@"  # Inicializa a impressora.
            b"\x1bt\x02"  # Seleciona a tabela PC850 para acentuação.
            b"\x1ba\x01\x1bE\x01"
            + titulo
            + b"\x1bE\x00\x1ba\x00"
            + corpo
            + b"\n\n\n\x1dV\x00"
        )

    def imprimir(self, dados: dict[str, Any], impressora: str | None = None):
        win32print = self._win32print()
        nome = (impressora or "").strip() or self.preferida() or self.padrao()
        if not nome:
            raise ErroImpressao("Nenhuma impressora foi selecionada.")

        handle = None
        doc = pagina = False
        try:
            handle = win32print.OpenPrinter(nome)
            win32print.StartDocPrinter(handle, 1, ("Aferição de pressão", None, "RAW"))
            doc = True
            win32print.StartPagePrinter(handle)
            pagina = True
            comprovante = self.montar_comprovante(dados)
            gravados = win32print.WritePrinter(handle, comprovante)
            if gravados != len(comprovante):
                raise OSError("O spooler recebeu o comprovante parcialmente.")
            self.salvar_preferida(nome)
        except Exception as erro:
            raise ErroImpressao(f"Não foi possível imprimir em '{nome}'.") from erro
        finally:
            if handle:
                if pagina:
                    try:
                        win32print.EndPagePrinter(handle)
                    except Exception:
                        pass
                if doc:
                    try:
                        win32print.EndDocPrinter(handle)
                    except Exception:
                        pass
                try:
                    win32print.ClosePrinter(handle)
                except Exception:
                    pass
