import customtkinter as ctk

from view.config import (
    BORDER_COLOR,
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    CARD_COLOR,
    FONT_FAMILY,
    TEXT_MUTED,
    aplicar_mascara_fixa,
    criar_input,
)


class AbaCadastro(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._status_after = None
        self.montar_ui()

    def montar_ui(self):
        centro = ctk.CTkFrame(
            self,
            width=820,
            fg_color=CARD_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        centro.pack(pady=(18, 20), padx=70, fill="x")

        ctk.CTkLabel(
            centro,
            text="CADASTRO RÁPIDO",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=BRAND_GREEN,
        ).pack(pady=(26, 2))

        ctk.CTkLabel(
            centro,
            text="Ficha do Cliente",
            font=(FONT_FAMILY, 28, "bold"),
        ).pack()
        ctk.CTkLabel(
            centro,
            text="Telefone e nome são obrigatórios. O endereço pode ficar em branco.",
            font=(FONT_FAMILY, 13),
            text_color=TEXT_MUTED,
        ).pack(pady=(4, 16))

        linha_telefone = ctk.CTkFrame(centro, fg_color="transparent")
        linha_telefone.pack(pady=(8, 6), padx=40, fill="x")

        self.entry_telefone = criar_input(
            linha_telefone,
            "Celular com DDD *",
            570,
        )
        self.entry_telefone.pack(
            side="left",
            padx=(0, 10),
            expand=True,
            fill="x",
        )
        self.entry_telefone.bind("<KeyRelease>", aplicar_mascara_fixa)
        self.entry_telefone.bind(
            "<Return>",
            lambda _event: self.controller.buscar_cliente(),
        )

        self.btn_buscar = ctk.CTkButton(
            linha_telefone,
            text="Buscar",
            width=135,
            height=50,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color="#444444",
            hover_color="#333333",
            corner_radius=8,
            command=self.controller.buscar_cliente,
        )
        self.btn_buscar.pack(side="left")

        self.entry_nome = criar_input(centro, "Nome completo *", 715)
        self.entry_endereco = criar_input(
            centro,
            "Endereço (opcional)",
            715,
        )

        self.entry_nome.pack(pady=7, padx=40, fill="x")
        self.entry_endereco.pack(pady=7, padx=40, fill="x")

        linha_endereco = ctk.CTkFrame(centro, fg_color="transparent")
        linha_endereco.pack(pady=7, padx=40, fill="x")

        self.entry_numero = criar_input(linha_endereco, "Número", 145)
        self.entry_bairro = criar_input(linha_endereco, "Bairro", 230)
        self.entry_complemento = criar_input(
            linha_endereco,
            "Complemento",
            300,
        )

        self.entry_numero.pack(side="left", padx=(0, 10))
        self.entry_bairro.pack(side="left", padx=(0, 10))
        self.entry_complemento.pack(side="left", expand=True, fill="x")

        self.entry_desejo = criar_input(
            centro,
            "Desejo / Faltou na loja (opcional)",
            715,
        )
        self.entry_desejo.pack(pady=7, padx=40, fill="x")

        acoes = ctk.CTkFrame(centro, fg_color="transparent")
        acoes.pack(pady=(18, 10), padx=40, fill="x")

        ctk.CTkButton(
            acoes,
            text="Limpar",
            width=130,
            height=54,
            font=(FONT_FAMILY, 14, "bold"),
            fg_color="#303A34",
            hover_color="#3B4840",
            corner_radius=10,
            command=self.limpar,
        ).pack(side="left", padx=(0, 10))

        self.btn_salvar = ctk.CTkButton(
            acoes,
            text="Salvar Cadastro",
            height=54,
            font=(FONT_FAMILY, 17, "bold"),
            fg_color=BRAND_GREEN,
            hover_color=BRAND_GREEN_HOVER,
            text_color="#081006",
            corner_radius=10,
            command=self.controller.salvar_cliente,
        )
        self.btn_salvar.pack(side="left", expand=True, fill="x")

        self.lbl_status = ctk.CTkLabel(
            centro,
            text="",
            height=34,
            corner_radius=8,
            text_color="white",
            font=(FONT_FAMILY, 13, "bold"),
        )
        self.lbl_status.pack(fill="x", padx=40, pady=(0, 22))

    def get_dados(self):
        return {
            "telefone": "".join(
                filter(str.isdigit, self.entry_telefone.get())
            ),
            "nome": self.entry_nome.get().strip(),
            "endereco": self.entry_endereco.get().strip(),
            "numero": self.entry_numero.get().strip(),
            "bairro": self.entry_bairro.get().strip(),
            "complemento": self.entry_complemento.get().strip(),
            "produto_desejo": self.entry_desejo.get().strip(),
        }

    def preencher(self, dados):
        self.limpar_dados()

        campos = (
            (self.entry_nome, "nome"),
            (self.entry_endereco, "endereco"),
            (self.entry_numero, "numero"),
            (self.entry_bairro, "bairro"),
            (self.entry_complemento, "complemento"),
            (self.entry_desejo, "produto_desejo"),
        )

        for campo, chave in campos:
            campo.insert(0, dados.get(chave) or "")

    def limpar_dados(self):
        campos = (
            self.entry_nome,
            self.entry_endereco,
            self.entry_numero,
            self.entry_bairro,
            self.entry_complemento,
            self.entry_desejo,
        )

        for campo in campos:
            campo.delete(0, "end")

    def limpar(self):
        self.entry_telefone.delete(0, "end")
        self.limpar_dados()
        self.entry_telefone.focus_set()

    def focar_nome(self):
        self.entry_nome.focus_set()

    def mostrar_status(self, mensagem, cor):
        if self._status_after:
            try:
                self.after_cancel(self._status_after)
            except Exception:
                pass

        if not mensagem:
            self.lbl_status.configure(text="", fg_color="transparent")
            return

        self.lbl_status.configure(text=mensagem, fg_color=cor)

        self._status_after = self.after(
            2800,
            lambda: self.lbl_status.configure(text="", fg_color="transparent"),
        )
