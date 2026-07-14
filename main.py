import csv
import logging
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

from fpdf import FPDF

from models.api_model import ErroAPI, FarmaciaAPI
from view.config import formatar_endereco, formatar_telefone, texto_opcional
from view.tela_principal import TelaFarmacia


PASTA_LOG = Path.home() / "PoupeFarma"
PASTA_LOG.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=PASTA_LOG / "poupe_farma.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("poupe_farma")


class FarmaciaController:
    COR_SUCESSO = "#7AC142"
    COR_AVISO = "#E5B800"
    COR_ERRO = "#D9534F"

    FILTROS = {
        "Hoje": "hoje",
        "Últimos 7 dias": "7dias",
        "Últimos 30 dias": "30dias",
        "Tudo": "tudo",
    }

    def __init__(self):
        self.api = FarmaciaAPI()
        self.view = TelaFarmacia(controller=self)
        self.clientes_cache = []
        self._carregamentos_ativos = 0

        self.view.after(150, self.carregar_clientes)
        self.view.after(250, self.carregar_fila)
        self.view.after(350, self.carregar_historico)

    def iniciar(self):
        self.view.mainloop()

    def _iniciar_carregamento(self):
        self._carregamentos_ativos += 1
        if self._carregamentos_ativos == 1:
            self.view.iniciar_carregamento()

    def _parar_carregamento(self):
        self._carregamentos_ativos = max(0, self._carregamentos_ativos - 1)
        if self._carregamentos_ativos == 0:
            self.view.parar_carregamento()

    def executar_thread(
        self,
        tarefa,
        sucesso=None,
        erro_status=None,
        carregamento=False,
    ):
        if carregamento:
            self._iniciar_carregamento()

        def executar():
            try:
                resultado = tarefa()
                self.view.after(0, lambda: self.view.atualizar_status_conexao(True))

                if sucesso:
                    self.view.after(0, lambda: sucesso(resultado))

            except ErroAPI as erro:
                mensagem = str(erro)
                logger.warning("Erro da API: %s", mensagem)

                if erro.status_code is None or erro.status_code >= 500:
                    self.view.after(
                        0,
                        lambda: self.view.atualizar_status_conexao(False),
                    )

                self.view.after(
                    0,
                    lambda: self.mostrar_erro(mensagem, erro_status),
                )

            except Exception:
                logger.exception("Erro inesperado")
                self.view.after(
                    0,
                    lambda: self.mostrar_erro(
                        "Ocorreu um erro inesperado. Consulte o log do sistema.",
                        erro_status,
                    ),
                )

            finally:
                if carregamento:
                    self.view.after(0, self._parar_carregamento)

        threading.Thread(target=executar, daemon=True).start()

    def mostrar_erro(self, mensagem, erro_status=None):
        if erro_status:
            erro_status(mensagem)

        messagebox.showerror(
            "Poupe Farma",
            mensagem,
            parent=self.view,
        )

    def mostrar_sucesso(self, mensagem):
        messagebox.showinfo(
            "Poupe Farma",
            mensagem,
            parent=self.view,
        )

    def obter_filtro(self):
        escolha = self.view.aba_historico.combo_filtro.get()
        return self.FILTROS.get(escolha, "hoje")

    def obter_tipo_historico(self):
        return self.view.aba_historico.combo_tipo.get()

    @staticmethod
    def texto_pdf(valor):
        return str(valor or "").encode(
            "latin-1",
            errors="replace",
        ).decode("latin-1")

    def buscar_cliente(self):
        dados = self.view.aba_cadastro.get_dados()
        telefone = dados.get("telefone", "").strip()

        if not telefone:
            self.view.aba_cadastro.mostrar_status(
                "Digite um telefone para pesquisar.",
                self.COR_AVISO,
            )
            return

        def sucesso(resposta):
            if resposta.get("encontrado"):
                self.view.aba_cadastro.preencher(resposta["dados"])
                self.view.aba_cadastro.mostrar_status(
                    "Cliente encontrado.",
                    self.COR_SUCESSO,
                )
            else:
                self.view.aba_cadastro.limpar_dados()
                self.view.aba_cadastro.mostrar_status(
                    "Novo cliente. Pode preencher.",
                    self.COR_AVISO,
                )

        self.executar_thread(
            lambda: self.api.buscar_cliente(telefone),
            sucesso=sucesso,
            erro_status=lambda msg: self.view.aba_cadastro.mostrar_status(
                msg,
                self.COR_ERRO,
            ),
            carregamento=True,
        )

    def _validar_cliente(self, dados):
        erros = []
        telefone = "".join(filter(str.isdigit, str(dados.get("telefone", ""))))
        nome = str(dados.get("nome", "")).strip()

        if not telefone:
            erros.append("telefone")
        elif len(telefone) not in (10, 11):
            erros.append("telefone com DDD")

        if not nome:
            erros.append("nome")

        return erros

    def salvar_cliente(self):
        dados = self.view.aba_cadastro.get_dados()
        faltando = self._validar_cliente(dados)

        if faltando:
            self.view.aba_cadastro.mostrar_status(
                "Preencha: " + ", ".join(faltando) + ".",
                self.COR_ERRO,
            )
            return

        def sucesso(_):
            self.view.aba_cadastro.mostrar_status(
                "Salvo com sucesso!",
                self.COR_SUCESSO,
            )
            self.carregar_clientes()

        self.executar_thread(
            lambda: self.api.salvar_cliente(dados),
            sucesso=sucesso,
            erro_status=lambda msg: self.view.aba_cadastro.mostrar_status(
                msg,
                self.COR_ERRO,
            ),
            carregamento=True,
        )

    def salvar_edicao_cliente(self, dados, ao_concluir=None):
        faltando = self._validar_cliente(dados)
        if faltando:
            self.mostrar_erro("Preencha: " + ", ".join(faltando) + ".")
            return

        def sucesso(_):
            if ao_concluir:
                ao_concluir()
            self.carregar_clientes()
            self.mostrar_sucesso("Cliente atualizado com sucesso.")

        self.executar_thread(
            lambda: self.api.salvar_cliente(dados),
            sucesso=sucesso,
            carregamento=True,
        )

    def carregar_clientes(self):
        def sucesso(clientes):
            self.clientes_cache = clientes
            self.view.aba_clientes.desenhar_lista(clientes)

        self.executar_thread(self.api.listar_clientes, sucesso=sucesso)

    def filtrar_clientes(self, event=None):
        pesquisa = self.view.aba_clientes.get_pesquisa()
        filtrados = [
            cliente
            for cliente in self.clientes_cache
            if pesquisa in str(cliente.get("nome", "")).lower()
            or pesquisa in str(cliente.get("telefone", ""))
        ]
        self.view.aba_clientes.desenhar_lista(filtrados)

    def excluir_cliente(self, telefone):
        confirmar = messagebox.askyesno(
            "Excluir cliente",
            "Deseja realmente excluir este cliente?",
            parent=self.view,
        )
        if not confirmar:
            return

        def sucesso(_):
            self.carregar_clientes()
            self.mostrar_sucesso("Cliente excluído com sucesso.")

        self.executar_thread(
            lambda: self.api.excluir_cliente(telefone),
            sucesso=sucesso,
            carregamento=True,
        )

    def lancar_entrega(self):
        busca, conteudo = self.view.aba_entregas.get_dados()

        if not busca or not conteudo:
            self.view.aba_entregas.mostrar_status(
                "Informe o cliente e adicione ao menos um produto.",
                self.COR_ERRO,
            )
            return

        def sucesso(_):
            self.view.aba_entregas.limpar()
            self.view.aba_entregas.mostrar_status(
                "Entrega lançada!",
                self.COR_SUCESSO,
            )
            self.carregar_fila()

        self.executar_thread(
            lambda: self.api.lancar_entrega(busca, conteudo),
            sucesso=sucesso,
            erro_status=lambda msg: self.view.aba_entregas.mostrar_status(
                msg,
                self.COR_ERRO,
            ),
            carregamento=True,
        )

    def carregar_fila(self):
        self.executar_thread(
            self.api.listar_pendentes,
            sucesso=self.view.aba_entregas.desenhar_fila,
        )

    def alterar_status(self, id_entrega, acao):
        mensagens = {
            "entregue": "Confirmar que a entrega foi realizada?",
            "cancelado": "Deseja realmente cancelar a entrega?",
        }

        if acao not in mensagens:
            self.mostrar_erro("Ação inválida para a entrega.")
            return

        if not messagebox.askyesno(
            "Confirmar ação",
            mensagens[acao],
            parent=self.view,
        ):
            return

        def sucesso(_):
            self.carregar_fila()
            self.carregar_historico()

        self.executar_thread(
            lambda: self.api.alterar_status_entrega(id_entrega, acao),
            sucesso=sucesso,
            carregamento=True,
        )

    def editar_conteudo_entrega(
        self,
        id_entrega,
        novo_conteudo,
        ao_concluir=None,
    ):
        novo_conteudo = novo_conteudo.strip()
        if not novo_conteudo:
            self.mostrar_erro("O conteúdo não pode ficar vazio.")
            return

        def sucesso(_):
            if ao_concluir:
                ao_concluir()
            self.carregar_fila()
            self.mostrar_sucesso("Entrega atualizada.")

        self.executar_thread(
            lambda: self.api.editar_conteudo_entrega(
                id_entrega,
                novo_conteudo,
            ),
            sucesso=sucesso,
            carregamento=True,
        )

    def mudar_filtro_historico(self, escolha=None):
        self.carregar_historico()

    def carregar_historico(self):
        if not hasattr(self.view, "aba_historico"):
            return

        filtro = self.obter_filtro()
        tipo = self.obter_tipo_historico()

        def tarefa():
            if tipo == "Histórico de Entregas":
                return "entregas", self.api.listar_historico(filtro)
            return "clientes", self.api.listar_logs_clientes(filtro)

        def sucesso(resultado):
            categoria, dados = resultado
            if categoria == "entregas":
                self.view.aba_historico.desenhar_entregas(dados)
            else:
                self.view.aba_historico.desenhar_log(dados)

        self.executar_thread(tarefa, sucesso=sucesso, carregamento=True)

    def exportar_excel(self):
        tipo = self.obter_tipo_historico()
        filtro = self.obter_filtro()
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            title="Salvar relatório",
            parent=self.view,
        )
        if not caminho:
            return

        def tarefa():
            dados = (
                self.api.listar_historico(filtro)
                if tipo == "Histórico de Entregas"
                else self.api.listar_logs_clientes(filtro)
            )

            with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.writer(arquivo, delimiter=";")

                if tipo == "Histórico de Entregas":
                    escritor.writerow(
                        [
                            "ID",
                            "Cliente",
                            "Telefone",
                            "Endereço",
                            "Mercadoria",
                            "Status",
                            "Data",
                        ]
                    )
                    for item in dados:
                        escritor.writerow(
                            [
                                item.get("id", ""),
                                item.get("nome_cliente", ""),
                                item.get("telefone", ""),
                                item.get("endereco", ""),
                                item.get("conteudo", ""),
                                item.get("status", ""),
                                item.get("data_formatada", ""),
                            ]
                        )
                else:
                    escritor.writerow(
                        [
                            "Nome",
                            "Telefone",
                            "Endereço",
                            "Número",
                            "Bairro",
                            "Complemento",
                            "Desejo",
                            "Data",
                        ]
                    )
                    for item in dados:
                        escritor.writerow(
                            [
                                item.get("nome", ""),
                                item.get("telefone", ""),
                                item.get("endereco", ""),
                                item.get("numero", ""),
                                item.get("bairro", ""),
                                item.get("complemento", ""),
                                item.get("produto_desejo", ""),
                                item.get("data_formatada", ""),
                            ]
                        )
            return caminho

        self.executar_thread(
            tarefa,
            sucesso=lambda arquivo: self.mostrar_sucesso(
                f"Relatório salvo em:\n\n{arquivo}"
            ),
            carregamento=True,
        )

    def exportar_pdf(self):
        tipo = self.obter_tipo_historico()
        filtro = self.obter_filtro()
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")],
            title="Salvar relatório",
            parent=self.view,
        )
        if not caminho:
            return

        def tarefa():
            dados = (
                self.api.listar_historico(filtro)
                if tipo == "Histórico de Entregas"
                else self.api.listar_logs_clientes(filtro)
            )

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(
                0,
                10,
                self.texto_pdf(f"Relatório: {tipo}"),
                ln=True,
                align="C",
            )
            pdf.ln(5)
            pdf.set_font("Arial", size=10)

            if not dados:
                pdf.multi_cell(0, 8, "Nenhum registro encontrado.")

            for item in dados:
                if tipo == "Histórico de Entregas":
                    texto = (
                        f"[{item.get('data_formatada', '')}] "
                        f"Pedido #{item.get('id', '')}\n"
                        f"Cliente: {item.get('nome_cliente', '')}\n"
                        f"Telefone: {formatar_telefone(item.get('telefone', ''))}\n"
                        f"Endereço: {texto_opcional(item.get('endereco'), 'Não informado')}\n"
                        f"Status: {item.get('status', '')}\n"
                        f"Itens: {item.get('conteudo', '')}"
                    )
                else:
                    texto = (
                        f"[{item.get('data_formatada', '')}] "
                        f"Cliente: {item.get('nome', '')}\n"
                        f"Telefone: {formatar_telefone(item.get('telefone', ''))}\n"
                        f"Endereço: {formatar_endereco(item)}\n"
                        f"Desejo: {item.get('produto_desejo', '')}"
                    )

                pdf.multi_cell(0, 7, self.texto_pdf(texto))
                pdf.ln(3)

            pdf.output(caminho)
            return caminho

        self.executar_thread(
            tarefa,
            sucesso=lambda arquivo: self.mostrar_sucesso(
                f"PDF salvo em:\n\n{arquivo}"
            ),
            carregamento=True,
        )


if __name__ == "__main__":
    try:
        app = FarmaciaController()
        app.iniciar()
    except Exception:
        logger.exception("Erro fatal ao iniciar o sistema.")
        raise
