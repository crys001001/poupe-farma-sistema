import logging
import os
import webbrowser
from tkinter import TclError

import customtkinter as ctk
from PIL import Image, ImageTk

from view.aba_afericao import AbaAfericao
from view.aba_cadastro import AbaCadastro
from view.aba_clientes import AbaClientes
from view.aba_entregas import AbaEntregas
from view.aba_historico import AbaHistorico
from view.config import (
    APP_NAME,
    APP_VERSION,
    BG_COLOR,
    BORDER_COLOR,
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    CARD_COLOR,
    FONT_FAMILY,
    INPUT_BG,
    SIDEBAR_COLOR,
    TEXT_COLOR,
    TEXT_MUTED,
    resource_path,
)

logger = logging.getLogger("sistema_cadastro")
ctk.set_appearance_mode("dark")


class JanelaSobre:
    def __init__(self, master):
        self.janela = ctk.CTkToplevel(master)
        self.janela.title(f"Sobre o {APP_NAME}")
        self.janela.geometry("500x660")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=BG_COLOR)
        self.janela.transient(master)
        self.janela.grab_set()

        caminho = resource_path(os.path.join("assets", "final_image.png"))
        try:
            imagem = Image.open(caminho)
            self._icone = ImageTk.PhotoImage(imagem)
            self._imagem = ctk.CTkImage(imagem, imagem, size=(220, 230))
            self.janela.after(10, lambda: self.janela.iconphoto(False, self._icone))
            ctk.CTkLabel(self.janela, text="", image=self._imagem).pack(pady=(18, 8))
        except (OSError, ValueError):
            logger.warning("Imagem da janela Sobre não encontrada: %s", caminho)

        dourado = "#E5B800"
        ctk.CTkLabel(
            self.janela, text=APP_NAME.upper(), font=("Impact", 30), text_color=dourado
        ).pack()
        ctk.CTkLabel(
            self.janela,
            text=f"SISTEMA DE CLIENTES, ENTREGAS E SERVIÇOS [v{APP_VERSION}]",
            font=("Consolas", 11, "bold"),
            text_color="#A0A0A0",
        ).pack(pady=(0, 14))

        dev = ctk.CTkFrame(
            self.janela,
            fg_color=CARD_COLOR,
            corner_radius=8,
            border_width=2,
            border_color=dourado,
        )
        dev.pack(padx=30, pady=10, fill="x")
        ctk.CTkLabel(
            dev, text="> DESENVOLVEDOR LÍDER:", font=("Consolas", 11, "bold"), text_color=dourado
        ).pack(pady=(14, 2))
        ctk.CTkLabel(
            dev, text="Crystyan Vicente Gomes de Arruda", font=(FONT_FAMILY, 18, "bold"), text_color="#00FF00"
        ).pack()
        ctk.CTkLabel(
            dev, text="Análise e Desenvolvimento de Sistemas (ADS)", font=("Consolas", 11, "italic"), text_color="#CCCCCC"
        ).pack(pady=(2, 14))

        links = ctk.CTkFrame(self.janela, fg_color="transparent")
        links.pack(pady=12)
        dados = (
            ("LinkedIn", "#0077B5", "https://www.linkedin.com/in/crystyan-vicente-92723a26b/"),
            ("GitHub", "#333333", "https://github.com/crys001001"),
            ("YouTube", "#CC0000", "https://www.youtube.com/@crystyanvicente7681"),
        )
        for coluna, (texto, cor, url) in enumerate(dados):
            ctk.CTkButton(
                links,
                text=texto,
                width=120,
                fg_color=cor,
                command=lambda destino=url: webbrowser.open(destino),
            ).grid(row=0, column=coluna, padx=5)

        ctk.CTkLabel(
            self.janela,
            text='"This is our new home. This is our heaven, and our hell.\nThis is Diamond Dogs."\n- Venom Snake',
            font=("Consolas", 12, "italic"),
            text_color="gray",
        ).pack(side="bottom", pady=18)


class TelaFarmacia(ctk.CTk):
    ABAS = ("Cadastro", "Clientes", "Entregas", "Aferição", "Histórico")
    DESCRICOES = {
        "Cadastro": "Cadastre ou localize um cliente pelo telefone.",
        "Clientes": "Consulte, edite e entre em contato com seus clientes.",
        "Entregas": "Monte pedidos e acompanhe a fila de entregas.",
        "Aferição": "Registre os valores e imprima o comprovante.",
        "Histórico": "Consulte movimentações e exporte relatórios.",
    }

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._icone = None
        self._aba_atual = None
        self._aviso_after = None
        self._versao_api = None
        self._frames = {}
        self._botoes = {}

        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.title(f"{APP_NAME} — Operação de balcão")
        self.configure(fg_color=BG_COLOR)

        try:
            self.state("zoomed")
        except TclError:
            pass

        self._configurar_windows()
        self._montar_interface()
        self._atalhos()
        self.mostrar_aba("Cadastro", avisar_controller=False)

    def _configurar_windows(self):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f"crystyan.sistemacadastro.app.{APP_VERSION}"
            )
        except (AttributeError, OSError):
            pass

        caminho = resource_path(os.path.join("assets", "final_image.png"))
        try:
            self._icone = ImageTk.PhotoImage(Image.open(caminho))
            self.iconphoto(False, self._icone)
        except (OSError, ValueError):
            logger.warning("Ícone não encontrado: %s", caminho)

    def _montar_interface(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(
            self,
            width=226,
            corner_radius=0,
            fg_color=SIDEBAR_COLOR,
            border_width=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)

        marca = ctk.CTkFrame(sidebar, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=22, pady=(26, 20))
        ctk.CTkLabel(
            marca,
            text=APP_NAME.upper(),
            font=(FONT_FAMILY, 17, "bold"),
            text_color=TEXT_COLOR,
        ).pack(anchor="w")
        ctk.CTkLabel(
            marca,
            text="OPERAÇÃO DE BALCÃO",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=BRAND_GREEN,
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(
            sidebar,
            height=1,
            fg_color=BORDER_COLOR,
        ).grid(row=1, column=0, sticky="ew", padx=18)

        nav = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="nsew", padx=12, pady=18)
        for indice, nome in enumerate(self.ABAS, start=1):
            botao = ctk.CTkButton(
                nav,
                text=f"F{indice}   {nome}",
                width=202,
                height=46,
                corner_radius=10,
                fg_color="transparent",
                hover_color=INPUT_BG,
                text_color=TEXT_MUTED,
                anchor="w",
                font=(FONT_FAMILY, 14, "bold"),
                command=lambda aba=nome: self.mostrar_aba(aba),
            )
            botao.pack(fill="x", pady=3)
            self._botoes[nome] = botao

        rodape = ctk.CTkFrame(
            sidebar,
            fg_color=CARD_COLOR,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        rodape.grid(row=3, column=0, sticky="ew", padx=14, pady=14)
        self.lbl_conexao = ctk.CTkLabel(
            rodape,
            text="●  Verificando servidor",
            height=30,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.lbl_conexao.pack(fill="x", padx=12, pady=(8, 2))
        linha_rodape = ctk.CTkFrame(rodape, fg_color="transparent")
        linha_rodape.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(
            linha_rodape,
            text=f"v{APP_VERSION}",
            text_color=TEXT_MUTED,
            font=(FONT_FAMILY, 11),
        ).pack(side="left")
        ctk.CTkButton(
            linha_rodape,
            text="Sobre",
            width=72,
            height=28,
            fg_color="transparent",
            hover_color=INPUT_BG,
            text_color=TEXT_MUTED,
            command=lambda: JanelaSobre(self),
        ).pack(side="right")

        principal = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        principal.grid(row=0, column=1, sticky="nsew")
        principal.grid_rowconfigure(1, weight=1)
        principal.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(principal, fg_color="transparent", height=78)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 4))
        header.grid_propagate(False)

        titulos = ctk.CTkFrame(header, fg_color="transparent")
        titulos.pack(side="left", fill="y")
        self.lbl_titulo = ctk.CTkLabel(
            titulos,
            text="",
            font=(FONT_FAMILY, 26, "bold"),
            text_color=TEXT_COLOR,
        )
        self.lbl_titulo.pack(anchor="w")
        self.lbl_subtitulo = ctk.CTkLabel(
            titulos,
            text="",
            font=(FONT_FAMILY, 13),
            text_color=TEXT_MUTED,
        )
        self.lbl_subtitulo.pack(anchor="w", pady=(2, 0))

        self.lbl_aviso = ctk.CTkLabel(
            principal,
            text="",
            height=38,
            corner_radius=10,
            font=(FONT_FAMILY, 13, "bold"),
        )

        self.conteudo = ctk.CTkFrame(principal, fg_color="transparent")
        self.conteudo.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        self.conteudo.grid_rowconfigure(0, weight=1)
        self.conteudo.grid_columnconfigure(0, weight=1)

        classes = {
            "Cadastro": AbaCadastro,
            "Clientes": AbaClientes,
            "Entregas": AbaEntregas,
            "Aferição": AbaAfericao,
            "Histórico": AbaHistorico,
        }
        for nome, classe in classes.items():
            frame = classe(self.conteudo, self.controller)
            frame.grid(row=0, column=0, sticky="nsew")
            self._frames[nome] = frame

        self.aba_cadastro = self._frames["Cadastro"]
        self.aba_clientes = self._frames["Clientes"]
        self.aba_entregas = self._frames["Entregas"]
        self.aba_afericao = self._frames["Aferição"]
        self.aba_historico = self._frames["Histórico"]

        self.barra_carregamento = ctk.CTkProgressBar(
            principal,
            mode="indeterminate",
            fg_color=CARD_COLOR,
            progress_color=BRAND_GREEN,
            height=6,
        )
        self.barra_carregamento.set(0)

    def _atalhos(self):
        for tecla, nome in zip(("<F1>", "<F2>", "<F3>", "<F4>", "<F5>"), self.ABAS):
            self.bind(tecla, lambda _e, aba=nome: self.mostrar_aba(aba))

    def mostrar_aba(self, nome, avisar_controller=True):
        if nome not in self._frames:
            return
        self._frames[nome].tkraise()
        self._aba_atual = nome
        self.lbl_titulo.configure(text=nome)
        self.lbl_subtitulo.configure(text=self.DESCRICOES[nome])
        for aba, botao in self._botoes.items():
            botao.configure(
                fg_color=BRAND_GREEN if aba == nome else "transparent",
                hover_color=BRAND_GREEN_HOVER if aba == nome else INPUT_BG,
                text_color="#091008" if aba == nome else TEXT_MUTED,
            )
        if avisar_controller:
            self.controller.ao_abrir_aba(nome)

    def notificar(self, mensagem, cor=BRAND_GREEN):
        if self._aviso_after:
            try:
                self.after_cancel(self._aviso_after)
            except Exception:
                pass
        self.lbl_aviso.configure(text=mensagem, fg_color=cor, text_color="white")
        self.lbl_aviso.place(relx=0.97, rely=0.025, anchor="ne")
        self.lbl_aviso.lift()
        self._aviso_after = self.after(2600, self.lbl_aviso.place_forget)

    def atualizar_status_conexao(self, conectado, versao=None):
        if versao:
            self._versao_api = versao

        texto_online = "●  Servidor online"
        if self._versao_api:
            texto_online += f" · API {self._versao_api}"

        self.lbl_conexao.configure(
            text=texto_online if conectado else "●  Servidor offline",
            text_color=BRAND_GREEN if conectado else "#FF6B6B",
        )

    def iniciar_carregamento(self):
        if not self.barra_carregamento.winfo_ismapped():
            self.barra_carregamento.place(
                x=28,
                y=106,
                relwidth=0.94,
            )
        self.barra_carregamento.start()

    def parar_carregamento(self):
        self.barra_carregamento.stop()
        self.barra_carregamento.place_forget()
