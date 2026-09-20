import csv
import logging
import queue
import threading
from pathlib import Path
from tkinter import TclError, filedialog, messagebox

from fpdf import FPDF

from models.api_model import ErroAPI, FarmaciaAPI
from models.impressora_model import ErroImpressao, ImpressoraTermica
from view.config import (
    APP_NAME,
    BRAND_GREEN,
    BRAND_RED,
    BRAND_YELLOW,
    formatar_endereco,
    formatar_telefone,
    texto_opcional,
)
from view.tela_principal import TelaFarmacia


PASTA_LOG = Path.home() / "SistemaCadastro"
PASTA_LOG.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=PASTA_LOG / "sistema_cadastro.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("sistema_cadastro")


class FarmaciaController:
    COR_SUCESSO = BRAND_GREEN
    COR_AVISO = BRAND_YELLOW
    COR_ERRO = BRAND_RED

    FILTROS = {
        "Hoje": "hoje",
        "Últimos 7 dias": "7dias",
        "Últimos 30 dias": "30dias",
        "Tudo": "tudo",
    }

    def __init__(self):
        self.api = FarmaciaAPI()
        self.impressora = ImpressoraTermica()
        self.view = TelaFarmacia(controller=self)
        self.clientes_cache = []
        self._carregamentos_ativos = 0
        self._tokens_solicitacao = {}
        self._fila_ui = queue.Queue()

        # Abertura rápida: só verifica a conexão. Listas e impressoras
        # são carregadas quando a aba correspondente é aberta.
        self.view.after(30, self._processar_fila_ui)
        self.view.after(120, self.verificar_servidor)

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

    def _agendar_ui(self, callback):
        """Entrega callbacks das workers para a thread principal do Tkinter."""
        self._fila_ui.put(callback)

    def _processar_fila_ui(self):
        try:
            while True:
                callback = self._fila_ui.get_nowait()
                try:
                    callback()
                except Exception:
                    logger.exception("Erro ao atualizar a interface")
        except queue.Empty:
            pass

        try:
            if self.view.winfo_exists():
                self.view.after(30, self._processar_fila_ui)
        except TclError:
            logger.info("Fila de interface encerrada com a janela.")

    def _novo_token(self, chave):
        token = self._tokens_solicitacao.get(chave, 0) + 1
        self._tokens_solicitacao[chave] = token
        return token

    def _token_atual(self, chave, token):
        return self._tokens_solicitacao.get(chave) == token

    def executar_thread(
        self,
        tarefa,
        sucesso=None,
        erro_status=None,
        carregamento=False,
        popup_erro=True,
        finalizar=None,
    ):
        if carregamento:
            self._iniciar_carregamento()

        def executar():
            try:
                resultado = tarefa()
                self._agendar_ui(lambda: self.view.atualizar_status_conexao(True))

                if sucesso:
                    self._agendar_ui(lambda: sucesso(resultado))

            except ErroAPI as erro:
                mensagem = str(erro)
                logger.warning("Erro da API: %s", mensagem)

                # Uma resposta HTTP, inclusive 4xx/5xx, confirma que o servidor
                # está acessível. Só erros sem status indicam falha de conexão.
                if erro.status_code is None:
                    self._agendar_ui(
                        lambda: self.view.atualizar_status_conexao(False)
                    )
                else:
                    self._agendar_ui(
                        lambda: self.view.atualizar_status_conexao(True)
                    )

                if popup_erro:
                    self._agendar_ui(
                        lambda: self.mostrar_erro(mensagem, erro_status)
                    )
                elif erro_status:
                    self._agendar_ui(lambda: erro_status(mensagem))

            except Exception:
                logger.exception("Erro inesperado")
                mensagem = "Ocorreu um erro inesperado. Consulte o log do sistema."
                if popup_erro:
                    self._agendar_ui(
                        lambda: self.mostrar_erro(mensagem, erro_status)
                    )
                elif erro_status:
                    self._agendar_ui(lambda: erro_status(mensagem))

            finally:
                if carregamento:
                    self._agendar_ui(self._parar_carregamento)
                if finalizar:
                    self._agendar_ui(finalizar)

        threading.Thread(target=executar, daemon=True).start()

    def mostrar_erro(self, mensagem, erro_status=None):
        if erro_status:
            erro_status(mensagem)

        messagebox.showerror(
            APP_NAME,
            mensagem,
            parent=self.view,
        )

    def mostrar_sucesso(self, mensagem):
        self.view.notificar(mensagem, self.COR_SUCESSO)

    def verificar_servidor(self):
        def sucesso(dados):
            versao = str(dados.get("versao") or "").strip() or None
            self.view.atualizar_status_conexao(True, versao)

            modulo = dados.get("modulos", {}).get("afericao")
            if modulo is False:
                self.view.aba_afericao.set_modulo_disponivel(
                    False,
                    "A tabela de aferições ainda não existe no servidor. "
                    "Aplique a migration antes de usar este módulo.",
                )

        self.executar_thread(
            self.api.verificar_saude,
            sucesso=sucesso,
            popup_erro=False,
            erro_status=lambda _msg: self.view.atualizar_status_conexao(False),
        )

    def ao_abrir_aba(self, nome):
        # Atualiza apenas o que o operador vai usar, evitando várias
        # requisições e pop-ups na inicialização.
        if nome == "Clientes":
            self.carregar_clientes()
        elif nome == "Entregas":
            self.carregar_fila()
        elif nome == "Aferição":
            self.view.aba_afericao.preparar_verificacao_modulo()
            self.atualizar_impressoras_afericao()
            self.carregar_afericoes()
        elif nome == "Histórico":
            self.carregar_historico()

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
                self.view.aba_cadastro.focar_nome()
                self.view.aba_cadastro.mostrar_status(
                    "Cliente encontrado.",
                    self.COR_SUCESSO,
                )
            else:
                self.view.aba_cadastro.limpar_dados()
                self.view.aba_cadastro.focar_nome()
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
        elif len(nome) > 100:
            erros.append("nome com até 100 caracteres")

        limites = (
            ("endereco", "endereço", 200),
            ("numero", "número", 20),
            ("bairro", "bairro", 100),
            ("complemento", "complemento", 150),
            ("produto_desejo", "desejo", 255),
        )
        for campo, rotulo, limite in limites:
            if len(str(dados.get(campo, "")).strip()) > limite:
                erros.append(f"{rotulo} com até {limite} caracteres")

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

        self.view.aba_cadastro.btn_salvar.configure(state="disabled")

        def sucesso(_):
            self.view.aba_cadastro.limpar()
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
            finalizar=lambda: self.view.aba_cadastro.btn_salvar.configure(
                state="normal"
            ),
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
        token = self._novo_token("clientes")

        def sucesso(clientes):
            if not self._token_atual("clientes", token):
                return
            self.clientes_cache = clientes
            if self.view.aba_clientes.get_pesquisa():
                self.filtrar_clientes()
            else:
                self.view.aba_clientes.desenhar_lista(clientes)

        self.executar_thread(self.api.listar_clientes, sucesso=sucesso)

    def filtrar_clientes(self, event=None):
        pesquisa = self.view.aba_clientes.get_pesquisa()
        pesquisa_digitos = "".join(filter(str.isdigit, pesquisa))

        filtrados = []
        for cliente in self.clientes_cache:
            nome = str(cliente.get("nome", "")).lower()
            telefone = "".join(
                filter(str.isdigit, str(cliente.get("telefone", "")))
            )
            if pesquisa in nome or (pesquisa_digitos and pesquisa_digitos in telefone):
                filtrados.append(cliente)

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

        if len(busca) > 100:
            self.view.aba_entregas.mostrar_status(
                "A busca do cliente deve ter até 100 caracteres.",
                self.COR_ERRO,
            )
            return

        if len(conteudo) > 4000:
            self.view.aba_entregas.mostrar_status(
                "O pedido ficou muito longo. Remova alguns itens.",
                self.COR_ERRO,
            )
            return

        self.view.aba_entregas.btn_lancar.configure(state="disabled")

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
            finalizar=lambda: self.view.aba_entregas.btn_lancar.configure(
                state="normal"
            ),
        )

    def carregar_fila(self):
        token = self._novo_token("fila")

        def sucesso(entregas):
            if self._token_atual("fila", token):
                self.view.aba_entregas.desenhar_fila(entregas)

        self.executar_thread(
            self.api.listar_pendentes,
            sucesso=sucesso,
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

    def atualizar_impressoras_afericao(self):
        token = self._novo_token("impressoras")
        self.view.aba_afericao.indicar_carregamento_impressoras()

        def tarefa():
            try:
                impressoras = self.impressora.listar()
                preferida = self.impressora.preferida() or self.impressora.padrao()
                return impressoras, preferida, None
            except ErroImpressao as erro:
                return [], None, str(erro)

        def sucesso(resultado):
            if not self._token_atual("impressoras", token):
                return
            impressoras, preferida, erro = resultado
            self.view.aba_afericao.set_impressoras(impressoras, preferida)
            if erro:
                self.view.aba_afericao.mostrar_status(erro, self.COR_ERRO)

        self.executar_thread(tarefa, sucesso=sucesso)

    def _validar_afericao(self, dados):
        valores = {}
        for campo, nome, minimo, maximo in (
            ("sistolica", "pressão sistólica", 30, 300),
            ("diastolica", "pressão diastólica", 20, 200),
            ("batimentos", "batimentos", 20, 300),
        ):
            valor = str(dados.get(campo, "")).strip()
            if not valor.isdigit() or not (minimo <= int(valor) <= maximo):
                return (
                    f"Informe um valor válido para {nome} "
                    f"({minimo} a {maximo})."
                )
            valores[campo] = int(valor)

        if valores["sistolica"] < valores["diastolica"]:
            return "A sistólica não pode ser menor que a diastólica. Confira o aparelho."

        telefone = str(dados.get("telefone", "")).strip()
        if telefone and len(telefone) not in (10, 11):
            return "Informe um telefone válido com DDD ou deixe o campo vazio."
        return None

    def registrar_afericao(self, imprimir=False):
        dados = self.view.aba_afericao.get_dados()
        erro = self._validar_afericao(dados)
        if erro:
            self.view.aba_afericao.mostrar_status(erro, self.COR_ERRO)
            return

        impressora = self.view.aba_afericao.get_impressora() if imprimir else None
        if imprimir and not impressora:
            self.view.aba_afericao.mostrar_status(
                "Selecione uma impressora para imprimir.",
                self.COR_ERRO,
            )
            return

        self.view.aba_afericao.set_registro_em_andamento(True)

        payload = {
            **dados,
            "sistolica": int(dados["sistolica"]),
            "diastolica": int(dados["diastolica"]),
            "batimentos": int(dados["batimentos"]),
        }

        def tarefa():
            registro = self.api.registrar_afericao(payload)
            erro_impressao = None
            if imprimir:
                try:
                    self.impressora.imprimir(registro, impressora)
                except ErroImpressao as erro:
                    erro_impressao = str(erro)
            return registro, erro_impressao

        def sucesso(resultado):
            _registro, erro_impressao = resultado
            self.view.aba_afericao.limpar()
            self.carregar_afericoes()

            if erro_impressao:
                self.mostrar_erro(
                    "A aferição foi registrada, mas a impressão falhou.\n\n"
                    + erro_impressao
                )
                return
            if imprimir:
                mensagem = "Aferição registrada e enviada para impressão."
            else:
                mensagem = "Aferição registrada com sucesso."

            self.view.aba_afericao.mostrar_status(mensagem, self.COR_SUCESSO)

        self.executar_thread(
            tarefa,
            sucesso=sucesso,
            erro_status=self._mostrar_erro_afericao,
            carregamento=True,
            popup_erro=False,
            finalizar=lambda: self.view.aba_afericao.set_registro_em_andamento(
                False
            ),
        )

    def _mostrar_erro_afericao(self, mensagem):
        mensagem_normalizada = mensagem.casefold()
        modulo_indisponivel = any(
            trecho in mensagem_normalizada
            for trecho in (
                "módulo de aferição indisponível",
                "tabela de aferições",
                "afericoes_pressao",
            )
        )

        if modulo_indisponivel:
            self.view.aba_afericao.set_modulo_disponivel(False, mensagem)
        else:
            self.view.aba_afericao.mostrar_status(
                mensagem,
                self.COR_ERRO,
            )

    def carregar_afericoes(self):
        if not hasattr(self.view, "aba_afericao"):
            return
        token = self._novo_token("afericoes")

        def sucesso(afericoes):
            if self._token_atual("afericoes", token):
                self.view.aba_afericao.set_modulo_disponivel(True)
                self.view.aba_afericao.desenhar_historico(afericoes)

        self.executar_thread(
            lambda: self.api.listar_afericoes("hoje"),
            sucesso=sucesso,
            erro_status=self._mostrar_erro_afericao,
            popup_erro=False,
        )

    def reimprimir_afericao(self, registro):
        impressora = self.view.aba_afericao.get_impressora()
        if not impressora:
            self.view.aba_afericao.mostrar_status(
                "Selecione uma impressora.",
                self.COR_ERRO,
            )
            return
        def tarefa():
            try:
                self.impressora.imprimir(registro, impressora)
                return None
            except ErroImpressao as erro:
                return str(erro)

        def sucesso(erro):
            if erro:
                self.mostrar_erro(erro)
            else:
                self.view.aba_afericao.mostrar_status(
                    "Comprovante enviado para impressão.",
                    self.COR_SUCESSO,
                )

        self.executar_thread(tarefa, sucesso=sucesso, carregamento=True)

    def mudar_filtro_historico(self, escolha=None):
        self.carregar_historico()

    def _dados_para_exportacao(self, tipo, filtro):
        if tipo == "Histórico de Entregas":
            return self.api.listar_historico(filtro, limite=5000)
        return self.api.listar_logs_clientes(filtro, limite=5000)

    def carregar_historico(self):
        if not hasattr(self.view, "aba_historico"):
            return

        filtro = self.obter_filtro()
        tipo = self.obter_tipo_historico()
        token = self._novo_token("historico")
        self.view.aba_historico.set_carregando(True)

        def tarefa():
            if tipo == "Histórico de Entregas":
                return "entregas", self.api.listar_historico(filtro)
            return "clientes", self.api.listar_logs_clientes(filtro)

        def sucesso(resultado):
            if not self._token_atual("historico", token):
                return
            categoria, dados = resultado
            if categoria == "entregas":
                self.view.aba_historico.desenhar_entregas(dados)
            else:
                self.view.aba_historico.desenhar_log(dados)

        def finalizar():
            if self._token_atual("historico", token):
                self.view.aba_historico.set_carregando(False)

        self.executar_thread(
            tarefa,
            sucesso=sucesso,
            finalizar=finalizar,
        )

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
            dados = self._dados_para_exportacao(tipo, filtro)

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
            dados = self._dados_para_exportacao(tipo, filtro)

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
