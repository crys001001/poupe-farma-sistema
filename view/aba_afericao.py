import customtkinter as ctk

from view.config import (
    BORDER_COLOR,
    BRAND_GREEN,
    BRAND_GREEN_HOVER,
    CARD_COLOR,
    FONT_FAMILY,
    INPUT_BG,
    TEXT_MUTED,
    aplicar_mascara_fixa,
    criar_input,
    formatar_telefone,
)


class AbaAfericao(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._status_after = None
        self._modulo_disponivel = None
        self.montar_ui()

    def montar_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        form = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        form.grid(row=0, column=0, sticky="nsew", padx=(24, 10), pady=18)

        ctk.CTkLabel(
            form,
            text="Aferição de Pressão",
            font=(FONT_FAMILY, 25, "bold"),
        ).pack(pady=(22, 4))
        ctk.CTkLabel(
            form,
            text="Use os valores completos do aparelho (ex.: 120 / 80).",
            font=(FONT_FAMILY, 12),
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 16))

        self.entry_nome = criar_input(form, "Cliente (opcional)", 300)
        self.entry_nome.pack(fill="x", padx=28, pady=5)

        self.entry_telefone = criar_input(form, "Telefone (opcional)", 300)
        self.entry_telefone.pack(fill="x", padx=28, pady=5)
        self.entry_telefone.bind("<KeyRelease>", aplicar_mascara_fixa)

        medidas = ctk.CTkFrame(form, fg_color="transparent")
        medidas.pack(fill="x", padx=23, pady=(12, 5))

        campos = (
            ("Sistólica", "mmHg", "entry_sistolica"),
            ("Diastólica", "mmHg", "entry_diastolica"),
            ("Batimentos", "bpm", "entry_batimentos"),
        )
        for titulo, unidade, atributo in campos:
            bloco = ctk.CTkFrame(medidas, fg_color="transparent")
            bloco.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(
                bloco,
                text=titulo,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=TEXT_MUTED,
            ).pack()
            entrada = ctk.CTkEntry(
                bloco,
                justify="center",
                height=58,
                font=(FONT_FAMILY, 24, "bold"),
                fg_color=INPUT_BG,
                border_width=0,
                corner_radius=8,
            )
            entrada.pack(fill="x", pady=(4, 2))
            ctk.CTkLabel(
                bloco,
                text=unidade,
                font=(FONT_FAMILY, 11),
                text_color=TEXT_MUTED,
            ).pack()
            setattr(self, atributo, entrada)

            entrada.bind("<KeyRelease>", self._limitar_medida)

        self.entry_sistolica.bind("<Return>", lambda _e: self.entry_diastolica.focus_set())
        self.entry_diastolica.bind("<Return>", lambda _e: self.entry_batimentos.focus_set())

        ctk.CTkLabel(
            form,
            text="Valor do serviço: R$ 5,00",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=BRAND_GREEN,
        ).pack(pady=(13, 8))

        impressao = ctk.CTkFrame(form, fg_color="transparent")
        impressao.pack(fill="x", padx=28, pady=5)
        self.combo_impressora = ctk.CTkComboBox(
            impressao,
            values=["Abra esta aba para carregar impressoras"],
            state="readonly",
            height=40,
            fg_color=INPUT_BG,
            border_width=0,
        )
        self.combo_impressora.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkButton(
            impressao,
            text="↻",
            width=42,
            height=40,
            fg_color="#444444",
            hover_color="#333333",
            command=self.controller.atualizar_impressoras_afericao,
        ).pack(side="right")

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.pack(fill="x", padx=28, pady=(10, 22))
        self.btn_registrar = ctk.CTkButton(
            botoes,
            text="Só registrar",
            height=48,
            fg_color="#444444",
            hover_color="#333333",
            state="disabled",
            command=lambda: self.controller.registrar_afericao(False),
        )
        self.btn_registrar.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.btn_imprimir = ctk.CTkButton(
            botoes,
            text="Registrar e imprimir",
            height=48,
            fg_color=BRAND_GREEN,
            hover_color=BRAND_GREEN_HOVER,
            font=(FONT_FAMILY, 15, "bold"),
            state="disabled",
            command=lambda: self.controller.registrar_afericao(True),
        )
        self.btn_imprimir.pack(side="left", expand=True, fill="x", padx=(5, 0))

        self.lbl_status = ctk.CTkLabel(
            form,
            text="",
            height=38,
            corner_radius=7,
            text_color="white",
            font=(FONT_FAMILY, 12, "bold"),
            wraplength=690,
            justify="center",
        )
        self.lbl_status.pack(fill="x", padx=28, pady=(0, 16))

        self.btn_revalidar = ctk.CTkButton(
            form,
            text="Testar integração novamente",
            height=36,
            fg_color="#344239",
            hover_color="#405248",
            command=self._revalidar_modulo,
        )

        historico = ctk.CTkFrame(self, fg_color="transparent")
        historico.grid(row=0, column=1, sticky="nsew", padx=(10, 24), pady=18)

        topo = ctk.CTkFrame(historico, fg_color="transparent")
        topo.pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(
            topo,
            text="Aferições de hoje",
            font=(FONT_FAMILY, 19, "bold"),
        ).pack(side="left")
        self.lbl_resumo = ctk.CTkLabel(topo, text="0 aferições • R$ 0,00", text_color=TEXT_MUTED)
        self.lbl_resumo.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(historico, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

    def get_dados(self):
        return {
            "nome_cliente": self.entry_nome.get().strip(),
            "telefone": "".join(filter(str.isdigit, self.entry_telefone.get())),
            "sistolica": self.entry_sistolica.get().strip(),
            "diastolica": self.entry_diastolica.get().strip(),
            "batimentos": self.entry_batimentos.get().strip(),
        }

    def get_impressora(self):
        nome = self.combo_impressora.get().strip()
        if not nome or nome.startswith(("Nenhuma", "Abra", "Carregando")):
            return None
        return nome

    @staticmethod
    def _limitar_medida(event):
        entrada = event.widget
        numeros = "".join(filter(str.isdigit, entrada.get()))[:3]
        if entrada.get() != numeros:
            entrada.delete(0, "end")
            entrada.insert(0, numeros)

    def indicar_carregamento_impressoras(self):
        texto = "Carregando impressoras..."
        self.combo_impressora.configure(values=[texto])
        self.combo_impressora.set(texto)
        self.btn_imprimir.configure(state="disabled")

    def set_registro_em_andamento(self, ativo):
        estado = (
            "disabled"
            if ativo or self._modulo_disponivel is not True
            else "normal"
        )
        self.btn_registrar.configure(state=estado)
        self.btn_imprimir.configure(
            state=(
                "disabled"
                if ativo
                or self._modulo_disponivel is not True
                or not self.get_impressora()
                else "normal"
            )
        )

    def preparar_verificacao_modulo(self):
        self._modulo_disponivel = None
        self.btn_revalidar.pack_forget()
        self.btn_registrar.configure(state="disabled")
        self.btn_imprimir.configure(state="disabled")
        self.mostrar_status(
            "Verificando integração com a API e o banco...",
            "#3B5163",
            temporario=False,
        )

    def set_modulo_disponivel(self, disponivel, mensagem=None):
        self._modulo_disponivel = bool(disponivel)
        self.btn_registrar.configure(
            state="normal" if self._modulo_disponivel else "disabled"
        )
        self.btn_imprimir.configure(
            state=(
                "normal"
                if self._modulo_disponivel and self.get_impressora()
                else "disabled"
            )
        )

        if self._modulo_disponivel:
            self.btn_revalidar.pack_forget()
            self.mostrar_status("", BRAND_GREEN)
        else:
            self.mostrar_status(
                mensagem or "Módulo de aferição indisponível no servidor.",
                "#B74343",
                temporario=False,
            )
            if not self.btn_revalidar.winfo_ismapped():
                self.btn_revalidar.pack(padx=28, pady=(0, 16), fill="x")

    def _revalidar_modulo(self):
        self.preparar_verificacao_modulo()
        self.controller.carregar_afericoes()

    def set_impressoras(self, impressoras, padrao=None):
        if not impressoras:
            texto = "Nenhuma impressora encontrada"
            self.combo_impressora.configure(values=[texto])
            self.combo_impressora.set(texto)
            self.btn_imprimir.configure(state="disabled")
            return
        self.combo_impressora.configure(values=impressoras)
        self.combo_impressora.set(padrao if padrao in impressoras else impressoras[0])
        self.btn_imprimir.configure(
            state="normal" if self._modulo_disponivel is True else "disabled"
        )

    def limpar(self):
        for campo in (
            self.entry_nome,
            self.entry_telefone,
            self.entry_sistolica,
            self.entry_diastolica,
            self.entry_batimentos,
        ):
            campo.delete(0, "end")
        self.entry_sistolica.focus_set()

    def mostrar_status(self, mensagem, cor, temporario=True):
        if self._status_after:
            try:
                self.after_cancel(self._status_after)
            except Exception:
                pass
        if not mensagem:
            self.lbl_status.configure(text="", fg_color="transparent")
            return
        self.lbl_status.configure(text=mensagem, fg_color=cor)
        if temporario:
            self._status_after = self.after(
                3000,
                lambda: self.lbl_status.configure(
                    text="", fg_color="transparent"
                ),
            )

    def desenhar_historico(self, afericoes):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        total = sum(float(item.get("valor") or 0) for item in afericoes)
        self.lbl_resumo.configure(
            text=f"{len(afericoes)} aferições • R$ {total:.2f}".replace(".", ",")
        )

        if not afericoes:
            ctk.CTkLabel(
                self.scroll,
                text="Nenhuma aferição registrada hoje.",
                font=(FONT_FAMILY, 14),
                text_color=TEXT_MUTED,
            ).pack(pady=50)
            return

        for item in afericoes:
            card = ctk.CTkFrame(self.scroll, fg_color=CARD_COLOR, corner_radius=9)
            card.pack(fill="x", pady=4)
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=12, pady=9)

            nome = item.get("nome_cliente") or "Sem identificação"
            ctk.CTkLabel(
                info,
                text=f"{nome}  •  {item.get('data_formatada', '')}",
                font=(FONT_FAMILY, 13, "bold"),
            ).pack(anchor="w")

            detalhe = (
                f"{item.get('sistolica', '')}/{item.get('diastolica', '')} mmHg"
                f"  •  {item.get('batimentos', '')} bpm"
            )
            telefone = item.get("telefone") or ""
            if telefone:
                detalhe += f"  •  {formatar_telefone(telefone)}"
            ctk.CTkLabel(info, text=detalhe, text_color=TEXT_MUTED, font=(FONT_FAMILY, 12)).pack(anchor="w", pady=(2, 0))

            ctk.CTkButton(
                card,
                text="Reimprimir",
                width=92,
                height=30,
                fg_color="#444444",
                hover_color="#333333",
                command=lambda dados=item: self.controller.reimprimir_afericao(dados),
            ).pack(side="right", padx=10)
