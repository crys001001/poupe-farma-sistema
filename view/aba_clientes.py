import customtkinter as ctk

from view.config import (
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    BRAND_RED,
    BRAND_RED_HOVER,
    BRAND_YELLOW,
    CARD_COLOR,
    INPUT_BG,
    TEXT_MUTED,
    abrir_whatsapp,
    criar_bloco_info,
    criar_input,
    criar_popup,
    formatar_endereco,
    formatar_telefone,
)


class AbaClientes(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self.montar_ui()

    def montar_ui(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(pady=(20, 10), fill="x", padx=40)

        self.entry_pesquisa = criar_input(
            topo,
            "Buscar por nome ou telefone...",
            550,
        )
        self.entry_pesquisa.pack(
            side="left",
            padx=(0, 10),
            expand=True,
            fill="x",
        )
        self.entry_pesquisa.bind(
            "<KeyRelease>",
            self.controller.filtrar_clientes,
        )

        ctk.CTkButton(
            topo,
            text="Atualizar lista",
            command=self.controller.carregar_clientes,
            width=130,
            height=50,
            font=("Arial", 14, "bold"),
            fg_color="#444444",
            hover_color="#333333",
        ).pack(side="right")

        self.scroll_lista = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.scroll_lista.pack(
            pady=5,
            padx=20,
            expand=True,
            fill="both",
        )

    def get_pesquisa(self):
        return self.entry_pesquisa.get().strip().lower()

    @staticmethod
    def _valor(valor):
        return str(valor or "").strip() or "Não informado"

    def abrir_dados(self, cliente):
        janela, card = criar_popup(
            self,
            "Detalhes do cliente",
            620,
            570,
        )

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=26, pady=(24, 12))

        ctk.CTkLabel(
            topo,
            text="CLIENTE",
            font=("Arial", 12, "bold"),
            text_color=BRAND_GREEN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            topo,
            text=self._valor(cliente.get("nome")),
            font=("Arial", 25, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        contato = ctk.CTkFrame(
            card,
            fg_color=INPUT_BG,
            corner_radius=10,
        )
        contato.pack(fill="x", padx=26, pady=(0, 12))

        textos = ctk.CTkFrame(contato, fg_color="transparent")
        textos.pack(
            side="left",
            fill="x",
            expand=True,
            padx=16,
            pady=13,
        )

        ctk.CTkLabel(
            textos,
            text="TELEFONE",
            font=("Arial", 10, "bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text=formatar_telefone(cliente.get("telefone", "")),
            font=("Arial", 17, "bold"),
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            contato,
            text="Abrir WhatsApp",
            width=130,
            height=38,
            fg_color="#25D366",
            hover_color="#128C7E",
            font=("Arial", 13, "bold"),
            command=lambda: abrir_whatsapp(cliente.get("telefone", "")),
        ).pack(side="right", padx=14)

        desejo = str(cliente.get("produto_desejo") or "").strip()

        criar_bloco_info(
            card,
            "ENDEREÇO",
            formatar_endereco(cliente),
        )
        criar_bloco_info(
            card,
            "DESEJO / FALTOU NA LOJA",
            desejo or "Não informado",
            BRAND_YELLOW if desejo else TEXT_MUTED,
        )

        ctk.CTkButton(
            card,
            text="Fechar",
            width=170,
            height=42,
            fg_color="#444444",
            hover_color="#333333",
            font=("Arial", 14, "bold"),
            command=janela.destroy,
        ).pack(pady=(18, 22))

    def abrir_edicao(self, cliente):
        janela, card = criar_popup(
            self,
            "Editar cliente",
            680,
            690,
        )

        ctk.CTkLabel(
            card,
            text="Editar cliente",
            font=("Arial", 26, "bold"),
            text_color=BRAND_GREEN,
        ).pack(pady=(24, 3))

        telefone = ctk.CTkFrame(card, fg_color=INPUT_BG, corner_radius=9)
        telefone.pack(fill="x", padx=30, pady=(8, 12))

        ctk.CTkLabel(
            telefone,
            text="TELEFONE CADASTRADO",
            font=("Arial", 10, "bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=14, pady=(10, 0))

        ctk.CTkLabel(
            telefone,
            text=formatar_telefone(cliente.get("telefone", "")),
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", padx=14, pady=(2, 10))

        formulario = ctk.CTkFrame(card, fg_color="transparent")
        formulario.pack(fill="x", padx=30)

        def campo(titulo, placeholder, valor):
            ctk.CTkLabel(
                formulario,
                text=titulo,
                font=("Arial", 12, "bold"),
            ).pack(anchor="w")

            entrada = criar_input(formulario, placeholder, 590)
            entrada.insert(0, valor or "")
            entrada.pack(fill="x", pady=(4, 12))
            return entrada

        e_nome = campo(
            "Nome completo *",
            "Nome completo",
            cliente.get("nome"),
        )
        e_endereco = campo(
            "Endereço (opcional)",
            "Rua ou avenida",
            cliente.get("endereco"),
        )

        linha = ctk.CTkFrame(formulario, fg_color="transparent")
        linha.pack(fill="x", pady=(0, 10))

        e_numero = criar_input(linha, "Número", 125)
        e_bairro = criar_input(linha, "Bairro", 190)
        e_complemento = criar_input(linha, "Complemento", 250)

        entradas = (
            (e_numero, cliente.get("numero")),
            (e_bairro, cliente.get("bairro")),
            (e_complemento, cliente.get("complemento")),
        )

        for entrada, valor in entradas:
            entrada.insert(0, valor or "")

        e_numero.pack(side="left", padx=(0, 8))
        e_bairro.pack(side="left", padx=(0, 8))
        e_complemento.pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(
            formulario,
            text="Desejo / Faltou na loja (opcional)",
            font=("Arial", 12, "bold"),
            text_color=BRAND_YELLOW,
        ).pack(anchor="w")

        e_desejo = criar_input(formulario, "Produto solicitado", 590)
        e_desejo.insert(0, cliente.get("produto_desejo") or "")
        e_desejo.pack(fill="x", pady=(4, 8))

        lbl_erro = ctk.CTkLabel(
            formulario,
            text="",
            text_color=BRAND_RED,
            font=("Arial", 12, "bold"),
        )
        lbl_erro.pack()

        def salvar():
            nome = e_nome.get().strip()

            if not nome:
                lbl_erro.configure(text="Informe o nome do cliente.")
                e_nome.focus_set()
                return

            dados = {
                "telefone": cliente.get("telefone", ""),
                "nome": nome,
                "endereco": e_endereco.get().strip(),
                "numero": e_numero.get().strip(),
                "bairro": e_bairro.get().strip(),
                "complemento": e_complemento.get().strip(),
                "produto_desejo": e_desejo.get().strip(),
            }

            self.controller.salvar_edicao_cliente(
                dados,
                ao_concluir=janela.destroy,
            )

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=30, pady=(10, 24))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            height=48,
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            command=janela.destroy,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6),
        )

        ctk.CTkButton(
            botoes,
            text="Salvar alterações",
            height=48,
            fg_color=BRAND_GREEN,
            hover_color=BRAND_GREEN_HOVER,
            font=("Arial", 15, "bold"),
            command=salvar,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(6, 0),
        )

        janela.after(100, e_nome.focus_set)

    def _mostrar_vazio(self, texto):
        ctk.CTkLabel(
            self.scroll_lista,
            text=texto,
            font=("Arial", 16),
            text_color=TEXT_MUTED,
        ).pack(pady=(70, 8))

        ctk.CTkLabel(
            self.scroll_lista,
            text="Cadastre um cliente ou altere a pesquisa.",
            font=("Arial", 13),
            text_color="#777777",
        ).pack()

    def desenhar_lista(self, lista):
        self._draw_id += 1
        desenho_atual = self._draw_id

        for widget in self.scroll_lista.winfo_children():
            widget.destroy()

        if not lista:
            self._mostrar_vazio("Nenhum cliente encontrado.")
            return

        def animar(index):
            if desenho_atual != self._draw_id or index >= len(lista):
                return

            cliente = lista[index]
            card = ctk.CTkFrame(
                self.scroll_lista,
                fg_color=CARD_COLOR,
                corner_radius=12,
            )
            card.pack(fill="x", pady=5, padx=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(
                side="left",
                fill="both",
                expand=True,
                padx=18,
                pady=12,
            )

            ctk.CTkLabel(
                info,
                text=cliente.get("nome", "Sem nome"),
                font=("Arial", 17, "bold"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=(
                    f"Telefone: {formatar_telefone(cliente.get('telefone', ''))}"
                    f"   |   {formatar_endereco(cliente)}"
                ),
                font=("Arial", 13),
                text_color=TEXT_MUTED,
                wraplength=900,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

            if cliente.get("produto_desejo"):
                ctk.CTkLabel(
                    info,
                    text=f"Faltou na loja: {cliente['produto_desejo']}",
                    font=("Arial", 13, "italic"),
                    text_color=BRAND_YELLOW,
                ).pack(anchor="w", pady=(2, 0))

            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=12, pady=8)

            acoes = (
                (
                    "Detalhes",
                    "#333333",
                    "#444444",
                    lambda cli=cliente: self.abrir_dados(cli),
                ),
                (
                    "Editar",
                    "#3A3A3A",
                    "#555555",
                    lambda cli=cliente: self.abrir_edicao(cli),
                ),
                (
                    "WhatsApp",
                    "#25D366",
                    "#128C7E",
                    lambda tel=cliente.get("telefone", ""): abrir_whatsapp(tel),
                ),
                (
                    "Excluir",
                    BRAND_RED,
                    BRAND_RED_HOVER,
                    lambda tel=cliente.get("telefone", ""): (
                        self.controller.excluir_cliente(tel)
                    ),
                ),
            )

            for posicao, (texto, cor, hover, comando) in enumerate(acoes):
                ctk.CTkButton(
                    botoes,
                    text=texto,
                    width=90,
                    height=30,
                    fg_color=cor,
                    hover_color=hover,
                    command=comando,
                ).grid(
                    row=posicao // 2,
                    column=posicao % 2,
                    padx=3,
                    pady=3,
                )

            self.after(8, lambda: animar(index + 1))

        animar(0)