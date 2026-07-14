import logging
import os
import webbrowser
from tkinter import TclError

import customtkinter as ctk
from PIL import Image, ImageTk

from view.aba_cadastro import AbaCadastro
from view.aba_clientes import AbaClientes
from view.aba_entregas import AbaEntregas
from view.aba_historico import AbaHistorico
from view.config import (
    APP_NAME,
    APP_VERSION,
    BG_COLOR,
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    CARD_COLOR,
    resource_path,
)


logger = logging.getLogger("poupe_farma")
ctk.set_appearance_mode("dark")


class JanelaSobre:
    def __init__(self, master):
        self.janela = ctk.CTkToplevel(master)
        self.janela.title(f"Sobre o {APP_NAME}")
        self.janela.geometry("500x680")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=BG_COLOR)
        self.janela.transient(master)
        self.janela.grab_set()

        self._carregar_imagem()

        cor_militar = "#E5B800"

        ctk.CTkLabel(
            self.janela,
            text=APP_NAME.upper(),
            font=("Impact", 32),
            text_color=cor_militar,
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            self.janela,
            text=(
                "SISTEMA INTEGRADO DE ENTREGAS "
                f"E LOGÍSTICA [v{APP_VERSION}]"
            ),
            font=("Consolas", 11, "bold"),
            text_color="#A0A0A0",
        ).pack(pady=(0, 15))

        dev = ctk.CTkFrame(
            self.janela,
            fg_color=CARD_COLOR,
            corner_radius=8,
            border_width=2,
            border_color=cor_militar,
        )
        dev.pack(pady=10, padx=30, fill="x")

        textos = (
            (
                "> DESENVOLVEDOR LÍDER:",
                ("Consolas", 11, "bold"),
                cor_militar,
            ),
            (
                "Crystyan Vicente Gomes de Arruda",
                ("Arial", 18, "bold"),
                "#00FF00",
            ),
            (
                "Análise e Desenvolvimento de Sistemas (ADS)",
                ("Consolas", 11, "italic"),
                "#CCCCCC",
            ),
        )

        for index, (texto, fonte, cor) in enumerate(textos):
            ctk.CTkLabel(
                dev,
                text=texto,
                font=fonte,
                text_color=cor,
            ).pack(
                pady=(15, 2)
                if index == 0
                else (2, 15)
                if index == 2
                else 2
            )

        links = ctk.CTkFrame(self.janela, fg_color="transparent")
        links.pack(pady=15)

        dados_links = (
            (
                "🔗 LinkedIn",
                "#0077B5",
                "#005582",
                "https://www.linkedin.com/in/"
                "crystyan-vicente-92723a26b/",
            ),
            (
                "💻 GitHub",
                "#333333",
                "#111111",
                "https://github.com/crys001001",
            ),
            (
                "▶️ YouTube",
                "#FF0000",
                "#CC0000",
                "https://www.youtube.com/@crystyanvicente7681",
            ),
        )

        for coluna, (texto, cor, hover, endereco) in enumerate(dados_links):
            ctk.CTkButton(
                links,
                text=texto,
                font=("Arial", 13, "bold"),
                fg_color=cor,
                hover_color=hover,
                width=120,
                command=lambda url=endereco: webbrowser.open(url),
            ).grid(row=0, column=coluna, padx=5)

        ctk.CTkLabel(
            self.janela,
            text=(
                '"This is our new home. This is our heaven, '
                'and our hell.\nThis is Diamond Dogs."\n'
                "- Venom Snake"
            ),
            font=("Consolas", 12, "italic"),
            text_color="gray",
        ).pack(side="bottom", pady=20)

    def _carregar_imagem(self):
        caminho = resource_path(
            os.path.join("assets", "final_image.png")
        )

        try:
            imagem = Image.open(caminho)
            self._icone = ImageTk.PhotoImage(imagem)
            self._imagem = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(240, 250),
            )

            self.janela.after(
                10,
                lambda: self.janela.iconphoto(False, self._icone),
            )

            ctk.CTkLabel(
                self.janela,
                text="",
                image=self._imagem,
            ).pack(pady=(20, 10))

        except (OSError, ValueError):
            logger.warning(
                "Imagem da janela Sobre não encontrada: %s",
                caminho,
            )

            ctk.CTkLabel(
                self.janela,
                text="[ IMAGEM NÃO ENCONTRADA ]",
                text_color="yellow",
            ).pack(pady=20)


class TelaFarmacia(ctk.CTk):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self._icone = None

        self.geometry("1100x780")
        self.minsize(960, 680)
        self.title("Sistema de Clientes e Entregas")
        self.configure(fg_color=BG_COLOR)

        try:
            self.state("zoomed")
        except TclError:
            logger.info("Maximização automática indisponível.")

        self._configurar_identidade_windows()
        self._configurar_icone()
        self._montar_interface()

    def _configurar_identidade_windows(self):
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "crystyan.poupefarma.app.1.0"
            )
        except (AttributeError, OSError):
            pass

    def _configurar_icone(self):
        caminho = resource_path(
            os.path.join("assets", "final_image.png")
        )

        try:
            self._icone = ImageTk.PhotoImage(Image.open(caminho))
            self.iconphoto(False, self._icone)
        except (OSError, ValueError):
            logger.warning("Ícone não encontrado: %s", caminho)

    def _montar_interface(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 0))

        self.lbl_conexao = ctk.CTkLabel(
            header,
            text="Conectando...",
            width=125,
            height=32,
            corner_radius=8,
            fg_color="#555555",
            text_color="white",
            font=("Arial", 12, "bold"),
        )
        self.lbl_conexao.pack(side="left")

        ctk.CTkButton(
            header,
            text="Sobre",
            width=120,
            height=35,
            fg_color="#333333",
            hover_color="#444444",
            font=("Arial", 12, "bold"),
            command=lambda: JanelaSobre(self),
        ).pack(side="right")

        self.tabview = ctk.CTkTabview(
            self,
            fg_color="transparent",
            segmented_button_fg_color=CARD_COLOR,
            segmented_button_selected_color=BRAND_GREEN,
            segmented_button_selected_hover_color=BRAND_GREEN_HOVER,
            segmented_button_unselected_color=CARD_COLOR,
            text_color="white",
        )
        self.tabview.pack(
            padx=20,
            pady=5,
            expand=True,
            fill="both",
        )
        self.tabview._segmented_button.configure(
            font=("Arial", 20, "bold")
        )

        abas = {
            "Cadastro": AbaCadastro,
            "Clientes": AbaClientes,
            "Entregas": AbaEntregas,
            "Histórico": AbaHistorico,
        }

        for nome in abas:
            self.tabview.add(nome)

        self.barra_carregamento = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            fg_color=CARD_COLOR,
            progress_color=BRAND_GREEN,
            height=8,
        )
        self.barra_carregamento.set(0)

        self.aba_cadastro = AbaCadastro(
            self.tabview.tab("Cadastro"),
            self.controller,
        )
        self.aba_clientes = AbaClientes(
            self.tabview.tab("Clientes"),
            self.controller,
        )
        self.aba_entregas = AbaEntregas(
            self.tabview.tab("Entregas"),
            self.controller,
        )
        self.aba_historico = AbaHistorico(
            self.tabview.tab("Histórico"),
            self.controller,
        )

        for aba in (
            self.aba_cadastro,
            self.aba_clientes,
            self.aba_entregas,
            self.aba_historico,
        ):
            aba.pack(fill="both", expand=True)

    def atualizar_status_conexao(self, conectado):
        self.lbl_conexao.configure(
            text="Servidor online" if conectado else "Servidor offline",
            fg_color="#1E6E43" if conectado else "#9A0007",
        )

    def iniciar_carregamento(self):
        if not self.barra_carregamento.winfo_ismapped():
            self.barra_carregamento.pack(
                fill="x",
                side="bottom",
                padx=20,
                pady=(0, 15),
            )

        self.barra_carregamento.start()

    def parar_carregamento(self):
        self.barra_carregamento.stop()
        self.barra_carregamento.pack_forget()