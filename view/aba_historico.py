import customtkinter as ctk

from view.config import (
    BRAND_GREEN,
    BRAND_RED,
    CARD_COLOR,
    INPUT_BG,
    TEXT_MUTED,
    abrir_whatsapp,
    criar_bloco_info,
    criar_popup,
    formatar_endereco,
    formatar_telefone,
    texto_opcional,
)


class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self.montar_ui()

    def montar_ui(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=40, pady=(20, 10))

        self.combo_tipo = ctk.CTkComboBox(
            topo,
            values=["Histórico de Entregas", "Log de Cadastros"],
            command=self.controller.mudar_filtro_historico,
            state="readonly",
            fg_color=INPUT_BG,
            border_width=0,
            width=210,
        )
        self.combo_tipo.set("Histórico de Entregas")
        self.combo_tipo.pack(side="left")

        self.combo_filtro = ctk.CTkComboBox(
            topo,
            values=["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Tudo"],
            command=self.controller.mudar_filtro_historico,
            state="readonly",
            fg_color=INPUT_BG,
            border_width=0,
            width=170,
        )
        self.combo_filtro.set("Hoje")
        self.combo_filtro.pack(side="left", padx=10)

        botoes = ctk.CTkFrame(topo, fg_color="transparent")
        botoes.pack(side="right")

        ctk.CTkButton(
            botoes,
            text="Exportar PDF",
            width=125,
            height=35,
            fg_color="#D32F2F",
            hover_color="#9A0007",
            command=self.controller.exportar_pdf,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botoes,
            text="Exportar CSV",
            width=125,
            height=35,
            fg_color="#1E6E43",
            hover_color="#154D2F",
            command=self.controller.exportar_excel,
        ).pack(side="left")

        self.scroll_hist = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.scroll_hist.pack(
            pady=5,
            padx=20,
            expand=True,
            fill="both",
        )

    def abrir_detalhes(self, pedido):
        janela, card = criar_popup(
            self,
            "Detalhes da entrega",
            630,
            590,
        )

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=26, pady=(23, 10))

        ctk.CTkLabel(
            topo,
            text=f"PEDIDO #{pedido.get('id', '')}",
            font=("Arial", 12, "bold"),
            text_color=BRAND_GREEN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            topo,
            text=pedido.get("nome_cliente") or "Cliente não informado",
            font=("Arial", 24, "bold"),
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
            font=("Arial", 10, "bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text=formatar_telefone(pedido.get("telefone", "")),
            font=("Arial", 16, "bold"),
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
        criar_bloco_info(
            card,
            "DATA",
            texto_opcional(
                pedido.get("data_formatada"),
                "Data não informada",
            ),
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

    def _limpar(self):
        for widget in self.scroll_hist.winfo_children():
            widget.destroy()

    def _mostrar_vazio(self, titulo, subtitulo):
        ctk.CTkLabel(
            self.scroll_hist,
            text=titulo,
            font=("Arial", 16),
            text_color=TEXT_MUTED,
        ).pack(pady=(70, 8))

        ctk.CTkLabel(
            self.scroll_hist,
            text=subtitulo,
            font=("Arial", 13),
            text_color="#777777",
        ).pack()

    def desenhar_entregas(self, historico):
        self._draw_id += 1
        desenho_atual = self._draw_id
        self._limpar()

        if not historico:
            self._mostrar_vazio(
                "Nenhuma entrega encontrada neste período.",
                "Altere o filtro ou finalize uma entrega.",
            )
            return

        def animar(index):
            if desenho_atual != self._draw_id or index >= len(historico):
                return

            entrega = historico[index]
            card = ctk.CTkFrame(
                self.scroll_hist,
                fg_color=CARD_COLOR,
                corner_radius=10,
            )
            card.pack(fill="x", pady=4, padx=10)

            cor = (
                BRAND_GREEN
                if entrega.get("status") == "Entregue"
                else BRAND_RED
            )

            ctk.CTkFrame(
                card,
                width=5,
                height=70,
                fg_color=cor,
                corner_radius=10,
            ).pack(side="left", padx=(0, 2), pady=5)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(
                side="left",
                fill="both",
                expand=True,
                padx=12,
                pady=9,
            )

            ctk.CTkLabel(
                info,
                text=(
                    f"Pedido #{entrega.get('id', '')} — "
                    f"{entrega.get('nome_cliente', '')}   "
                    f"{entrega.get('data_formatada', 'N/A')}"
                ),
                font=("Arial", 15, "bold"),
                anchor="w",
            ).pack(fill="x")

            ctk.CTkLabel(
                info,
                text=(
                    f"{str(entrega.get('status', '')).upper()}  •  "
                    f"{entrega.get('conteudo', '')}"
                ),
                font=("Arial", 13),
                text_color=TEXT_MUTED,
                anchor="w",
                wraplength=1100,
                justify="left",
            ).pack(fill="x", pady=(3, 0))

            ctk.CTkButton(
                card,
                text="Detalhes",
                width=85,
                height=32,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda ped=entrega: self.abrir_detalhes(ped),
            ).pack(side="right", padx=12)

            self.after(8, lambda: animar(index + 1))

        animar(0)

    def desenhar_log(self, cadastros):
        self._draw_id += 1
        desenho_atual = self._draw_id
        self._limpar()

        if not cadastros:
            self._mostrar_vazio(
                "Nenhum cadastro encontrado neste período.",
                "Altere o filtro ou cadastre um cliente.",
            )
            return

        def animar(index):
            if desenho_atual != self._draw_id or index >= len(cadastros):
                return

            cadastro = cadastros[index]
            card = ctk.CTkFrame(
                self.scroll_hist,
                fg_color=CARD_COLOR,
                corner_radius=10,
            )
            card.pack(fill="x", pady=4, padx=10)

            ctk.CTkFrame(
                card,
                width=5,
                height=66,
                fg_color="#007ACC",
                corner_radius=10,
            ).pack(side="left", padx=(0, 2), pady=5)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(
                side="left",
                fill="both",
                expand=True,
                padx=12,
                pady=9,
            )

            ctk.CTkLabel(
                info,
                text=(
                    f"{cadastro.get('nome', '')}   "
                    f"{cadastro.get('data_formatada', 'N/A')}"
                ),
                font=("Arial", 15, "bold"),
                anchor="w",
            ).pack(fill="x")

            ctk.CTkLabel(
                info,
                text=(
                    f"Telefone: "
                    f"{formatar_telefone(cadastro.get('telefone', ''))}"
                    f"  •  {formatar_endereco(cadastro)}"
                ),
                font=("Arial", 13),
                text_color=TEXT_MUTED,
                anchor="w",
                wraplength=1100,
                justify="left",
            ).pack(fill="x", pady=(3, 0))

            self.after(8, lambda: animar(index + 1))

        animar(0)