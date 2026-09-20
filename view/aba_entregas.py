import customtkinter as ctk

from view.config import (
    BORDER_COLOR,
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    BRAND_RED,
    CARD_COLOR,
    FONT_FAMILY,
    INPUT_BG,
    TEXT_MUTED,
    abrir_whatsapp,
    criar_bloco_info,
    criar_input,
    criar_popup,
    formatar_telefone,
    texto_opcional,
)


class AbaEntregas(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self._status_after = None
        self.itens_carrinho = []
        self.montar_ui()

    def montar_ui(self):
        lancamento = ctk.CTkFrame(
            self,
            width=800,
            fg_color=CARD_COLOR,
            corner_radius=15,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        lancamento.pack(pady=(12, 14), padx=30, fill="x")

        ctk.CTkLabel(
            lancamento,
            text="NOVA ENTREGA",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=BRAND_GREEN,
        ).pack(anchor="w", padx=30, pady=(18, 0))

        self.entry_busca = criar_input(
            lancamento,
            "Nome ou telefone...",
            700,
        )
        self.entry_busca.pack(pady=(10, 10), padx=30, fill="x")

        linha_item = ctk.CTkFrame(lancamento, fg_color="transparent")
        linha_item.pack(pady=5, padx=30, fill="x")

        self.e_qtd = criar_input(linha_item, "Qtd", 100)
        self.e_prod = criar_input(linha_item, "Nome do produto", 440)

        self.e_qtd.pack(side="left", padx=(0, 10))
        self.e_prod.pack(
            side="left",
            padx=(0, 10),
            expand=True,
            fill="x",
        )
        self.e_prod.bind(
            "<Return>",
            lambda _event: self.adicionar_item(),
        )

        ctk.CTkButton(
            linha_item,
            text="Adicionar",
            width=140,
            height=50,
            font=(FONT_FAMILY, 16, "bold"),
            fg_color="#444444",
            hover_color="#333333",
            command=self.adicionar_item,
        ).pack(side="right")

        cabecalho_itens = ctk.CTkFrame(lancamento, fg_color="transparent")
        cabecalho_itens.pack(fill="x", padx=30, pady=(10, 2))
        ctk.CTkLabel(
            cabecalho_itens,
            text="ITENS DO PEDIDO",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left")
        self.lbl_total_itens = ctk.CTkLabel(
            cabecalho_itens,
            text="0 itens",
            font=(FONT_FAMILY, 11),
            text_color=TEXT_MUTED,
        )
        self.lbl_total_itens.pack(side="right")

        self.box_itens = ctk.CTkScrollableFrame(
            lancamento,
            fg_color=INPUT_BG,
            height=82,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.box_itens.pack(fill="x", padx=30, pady=(2, 8))
        self._desenhar_itens()

        self.btn_lancar = ctk.CTkButton(
            lancamento,
            text="Lançar Entrega",
            command=self.controller.lancar_entrega,
            height=55,
            font=(FONT_FAMILY, 18, "bold"),
            fg_color=BRAND_GREEN,
            hover_color=BRAND_GREEN_HOVER,
        )
        self.btn_lancar.pack(pady=(4, 8), padx=30, fill="x")

        self.lbl_status = ctk.CTkLabel(
            self,
            text="",
            height=34,
            corner_radius=8,
            text_color="white",
            font=(FONT_FAMILY, 13, "bold"),
        )
        self.lbl_status.pack(fill="x", padx=30, pady=(0, 16))

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=40)

        self.lbl_pendentes = ctk.CTkLabel(
            topo,
            text="Pedidos pendentes",
            font=(FONT_FAMILY, 18, "bold"),
        )
        self.lbl_pendentes.pack(side="left")

        ctk.CTkButton(
            topo,
            text="Atualizar lista",
            command=self.controller.carregar_fila,
            width=120,
            height=32,
            fg_color="#444444",
            hover_color="#333333",
        ).pack(side="right")

        self.scroll_fila = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.scroll_fila.pack(
            pady=5,
            expand=True,
            fill="both",
        )

    def adicionar_item(self):
        quantidade = self.e_qtd.get().strip() or "1"
        produto = self.e_prod.get().strip()

        if not produto:
            self.mostrar_status("Informe o nome do produto.", BRAND_RED)
            return

        if not quantidade.isdigit() or not (1 <= int(quantidade) <= 999):
            self.mostrar_status("Informe uma quantidade entre 1 e 999.", BRAND_RED)
            return

        if len(produto) > 120:
            self.mostrar_status("O nome do produto deve ter até 120 caracteres.", BRAND_RED)
            return

        if len(self.itens_carrinho) >= 50:
            self.mostrar_status("O pedido atingiu o limite de 50 itens.", BRAND_RED)
            return

        self.itens_carrinho.append(f"{int(quantidade)}x {produto}")
        self._desenhar_itens()

        self.e_qtd.delete(0, "end")
        self.e_prod.delete(0, "end")
        self.e_prod.focus_set()

    def remover_item(self, index):
        if 0 <= index < len(self.itens_carrinho):
            self.itens_carrinho.pop(index)
            self._desenhar_itens()

    def _desenhar_itens(self):
        for widget in self.box_itens.winfo_children():
            widget.destroy()

        quantidade = len(self.itens_carrinho)
        self.lbl_total_itens.configure(
            text=f"{quantidade} item" if quantidade == 1 else f"{quantidade} itens"
        )

        if not self.itens_carrinho:
            ctk.CTkLabel(
                self.box_itens,
                text="Nenhum produto adicionado.",
                text_color=TEXT_MUTED,
                font=(FONT_FAMILY, 13),
            ).pack(pady=18)
            return

        for index, texto in enumerate(self.itens_carrinho):
            item = ctk.CTkFrame(
                self.box_itens,
                fg_color="#29352E",
                corner_radius=8,
            )
            item.pack(fill="x", padx=4, pady=3)

            ctk.CTkLabel(
                item,
                text=texto,
                font=(FONT_FAMILY, 13),
                anchor="w",
            ).pack(side="left", padx=10, pady=6, fill="x", expand=True)

            ctk.CTkButton(
                item,
                text="Remover",
                width=70,
                height=28,
                fg_color="transparent",
                hover_color="#4A3434",
                text_color="#FF8585",
                command=lambda i=index: self.remover_item(i),
            ).pack(side="right", padx=6, pady=3)

    def get_dados(self):
        return (
            self.entry_busca.get().strip(),
            " / ".join(self.itens_carrinho),
        )

    def limpar(self):
        for campo in (self.entry_busca, self.e_qtd, self.e_prod):
            campo.delete(0, "end")

        self.itens_carrinho.clear()
        self._desenhar_itens()

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
            2500,
            lambda: self.lbl_status.configure(text="", fg_color="transparent"),
        )

    def abrir_detalhes(self, pedido):
        janela, card = criar_popup(
            self,
            "Detalhes da entrega",
            620,
            545,
        )

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=26, pady=(23, 10))

        ctk.CTkLabel(
            topo,
            text=f"PEDIDO #{pedido.get('id', '')}",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=BRAND_GREEN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            topo,
            text=pedido.get("nome_cliente") or "Cliente não informado",
            font=(FONT_FAMILY, 24, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        contato = ctk.CTkFrame(
            card,
            fg_color=INPUT_BG,
            corner_radius=10,
        )
        contato.pack(fill="x", padx=26, pady=6)

        textos = ctk.CTkFrame(contato, fg_color="transparent")
        textos.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=12,
        )

        ctk.CTkLabel(
            textos,
            text="TELEFONE",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text=formatar_telefone(pedido.get("telefone", "")),
            font=(FONT_FAMILY, 16, "bold"),
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            contato,
            text="WhatsApp",
            width=110,
            height=36,
            fg_color="#25D366",
            hover_color="#128C7E",
            command=lambda: abrir_whatsapp(pedido.get("telefone", "")),
        ).pack(side="right", padx=14)

        criar_bloco_info(
            card,
            "ENDEREÇO",
            texto_opcional(
                pedido.get("endereco"),
                "Endereço não informado",
            ),
        )
        criar_bloco_info(
            card,
            "ITENS",
            texto_opcional(
                pedido.get("conteudo"),
                "Nenhum item informado",
            ),
            "#FFCC00",
            True,
        )

        ctk.CTkButton(
            card,
            text="Fechar",
            width=170,
            height=42,
            fg_color="#444444",
            hover_color="#333333",
            command=janela.destroy,
        ).pack(pady=(16, 22))

    def abrir_edicao(self, pedido):
        janela, card = criar_popup(
            self,
            "Editar entrega",
            570,
            350,
        )

        ctk.CTkLabel(
            card,
            text=f"Editar pedido #{pedido.get('id', '')}",
            font=(FONT_FAMILY, 23, "bold"),
            text_color=BRAND_GREEN,
        ).pack(pady=(23, 4))

        entry_edit = criar_input(card, "Conteúdo da entrega", 480)
        entry_edit.insert(0, pedido.get("conteudo") or "")
        entry_edit.pack(padx=25, pady=(20, 5), fill="x")

        lbl_erro = ctk.CTkLabel(
            card,
            text="",
            text_color=BRAND_RED,
            font=(FONT_FAMILY, 12, "bold"),
        )
        lbl_erro.pack()

        def salvar():
            conteudo = entry_edit.get().strip()

            if not conteudo:
                lbl_erro.configure(
                    text="Informe o conteúdo da entrega."
                )
                return

            self.controller.editar_conteudo_entrega(
                pedido["id"],
                conteudo,
                ao_concluir=janela.destroy,
            )

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=25, pady=(13, 22))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            height=44,
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            command=janela.destroy,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5),
        )

        ctk.CTkButton(
            botoes,
            text="Salvar alteração",
            height=44,
            fg_color=BRAND_GREEN,
            hover_color=BRAND_GREEN_HOVER,
            command=salvar,
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0),
        )

        janela.after(100, entry_edit.focus_set)

    def desenhar_fila(self, entregas):
        self._draw_id += 1
        desenho_atual = self._draw_id

        for widget in self.scroll_fila.winfo_children():
            widget.destroy()

        quantidade = len(entregas)
        self.lbl_pendentes.configure(
            text=(
                f"{quantidade} pedido pendente"
                if quantidade == 1
                else f"{quantidade} pedidos pendentes"
            )
        )

        if not entregas:
            ctk.CTkLabel(
                self.scroll_fila,
                text="Nenhuma entrega pendente.",
                font=(FONT_FAMILY, 16),
                text_color=TEXT_MUTED,
            ).pack(pady=60)
            return

        def animar(index):
            if desenho_atual != self._draw_id or index >= len(entregas):
                return

            entrega = entregas[index]
            card = ctk.CTkFrame(
                self.scroll_fila,
                fg_color=CARD_COLOR,
                corner_radius=10,
                border_width=1,
                border_color=BORDER_COLOR,
            )
            card.pack(fill="x", pady=6, padx=10)

            ctk.CTkFrame(
                card,
                width=5,
                height=72,
                fg_color=BRAND_GREEN,
                corner_radius=10,
            ).pack(side="left", padx=(0, 2), pady=5)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(
                side="left",
                fill="both",
                expand=True,
                padx=12,
                pady=10,
            )

            ctk.CTkLabel(
                info,
                text=(
                    f"#{entrega.get('id', '')} - "
                    f"{entrega.get('nome_cliente', '')}  •  "
                    f"{formatar_telefone(entrega.get('telefone', ''))}  •  "
                    f"{entrega.get('data_formatada', '')}"
                ),
                font=(FONT_FAMILY, 16, "bold"),
                anchor="w",
            ).pack(fill="x")

            ctk.CTkLabel(
                info,
                text=f"Itens: {entrega.get('conteudo', '')}",
                font=(FONT_FAMILY, 14),
                text_color=TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=620,
            ).pack(fill="x", pady=(5, 0))

            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)

            acoes = (
                (
                    "WhatsApp",
                    "#25D366",
                    "#128C7E",
                    lambda tel=entrega.get("telefone", ""): abrir_whatsapp(tel),
                ),
                (
                    "Detalhes",
                    "#333333",
                    "#444444",
                    lambda ped=entrega: self.abrir_detalhes(ped),
                ),
                (
                    "Editar",
                    "#333333",
                    "#444444",
                    lambda ped=entrega: self.abrir_edicao(ped),
                ),
                (
                    "Entregue",
                    BRAND_GREEN,
                    BRAND_GREEN_HOVER,
                    lambda ident=entrega.get("id"): (
                        self.controller.alterar_status(ident, "entregue")
                    ),
                ),
                (
                    "Cancelar",
                    BRAND_RED,
                    "#9A0007",
                    lambda ident=entrega.get("id"): (
                        self.controller.alterar_status(ident, "cancelado")
                    ),
                ),
            )

            for posicao, (texto, cor, hover, comando) in enumerate(acoes):
                linha = 0 if posicao < 3 else 1
                coluna = posicao if posicao < 3 else posicao - 2

                ctk.CTkButton(
                    botoes,
                    text=texto,
                    width=90,
                    height=35,
                    fg_color=cor,
                    hover_color=hover,
                    command=comando,
                ).grid(
                    row=linha,
                    column=coluna,
                    padx=3,
                    pady=3,
                )

            self.after(8, lambda: animar(index + 1))

        animar(0)
