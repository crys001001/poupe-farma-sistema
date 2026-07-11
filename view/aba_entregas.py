import customtkinter as ctk
from view.config import BRAND_GREEN, BRAND_GREEN_HOVER, BRAND_RED, BRAND_RED_HOVER, BG_COLOR, CARD_COLOR, INPUT_BG, criar_input, abrir_whatsapp

class AbaEntregas(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self.itens_carrinho = []
        self.montar_ui()

    def montar_ui(self):
        container_lancamento = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=15, width=800)
        container_lancamento.pack(pady=(30, 20), padx=40)
        
        ctk.CTkLabel(container_lancamento, text="NOVA ENTREGA", font=("Arial", 12, "bold"), text_color="#aaaaaa").pack(anchor="w", padx=30, pady=(20, 0))
        
        self.entry_busca = criar_input(container_lancamento, "Nome ou Telefone...", width=700)
        self.entry_busca.pack(pady=(10, 10), padx=30, fill="x")
        
        f_add = ctk.CTkFrame(container_lancamento, fg_color="transparent")
        f_add.pack(pady=5, padx=30, fill="x")
        
        self.e_qtd = criar_input(f_add, "Qtd", 100)
        self.e_qtd.pack(side="left", padx=(0, 10))
        self.e_prod = criar_input(f_add, "Nome do Produto (Ex: Dipirona)", 440)
        self.e_prod.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.e_prod.bind("<Return>", lambda e: self.adicionar_item())
        
        ctk.CTkButton(f_add, text="Adicionar", width=140, height=50, font=("Arial", 16, "bold"), fg_color="#444444", hover_color="#333333", command=self.adicionar_item).pack(side="right")
        
        self.box_itens = ctk.CTkFrame(container_lancamento, fg_color=INPUT_BG, height=70, corner_radius=8)
        self.box_itens.pack(fill="x", padx=30, pady=10)
        self.box_itens.pack_propagate(False)

        ctk.CTkButton(container_lancamento, text="Lançar Entrega", command=self.controller.lancar_entrega, height=55, font=("Arial", 18, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=8).pack(pady=(5, 20), padx=30, fill="x")
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.lbl_status.pack()

        top_fila = ctk.CTkFrame(self, fg_color="transparent")
        top_fila.pack(fill="x", padx=40)
        ctk.CTkLabel(top_fila, text="Pedidos Pendentes", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkButton(top_fila, text="Atualizar", command=self.controller.carregar_fila, width=100, height=30, fg_color="#444444", hover_color="#333333", corner_radius=6).pack(side="right")
        
        self.scroll_fila = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_fila.pack(pady=5, expand=True, fill="both")

    def adicionar_item(self):
        qtd = self.e_qtd.get() or "1"
        prod = self.e_prod.get().strip()
        if prod:
            texto = f"{qtd}x {prod}"
            self.itens_carrinho.append(texto)
            badge = ctk.CTkFrame(self.box_itens, fg_color="#333333", border_width=1, border_color="#555555", corner_radius=6)
            badge.pack(side="left", padx=5, pady=10)
            ctk.CTkLabel(badge, text=texto, font=("Arial", 12)).pack(padx=10, pady=5)
            self.e_qtd.delete(0, 'end')
            self.e_prod.delete(0, 'end')

    def get_dados(self): 
        return self.entry_busca.get(), " / ".join(self.itens_carrinho)

    def limpar(self): 
        self.entry_busca.delete(0, 'end')
        self.itens_carrinho.clear()
        for w in self.box_itens.winfo_children(): w.destroy()

    def mostrar_status(self, msg, cor): 
        self.lbl_status.configure(text=msg, text_color=cor)

    def abrir_detalhes(self, pedido):
        janela = ctk.CTkToplevel(self)
        janela.title("Ficha da Entrega")
        janela.geometry("450x380")
        janela.configure(fg_color=BG_COLOR)
        janela.attributes("-topmost", True) 
        frame = ctk.CTkFrame(janela, fg_color=CARD_COLOR, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="DETALHES DO PEDIDO", font=("Arial", 14, "bold"), text_color=BRAND_GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(frame, text=f"👤 {pedido['nome_cliente']}", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=5)
        
        frame_tel = ctk.CTkFrame(frame, fg_color="transparent")
        frame_tel.pack(anchor="w", padx=20, pady=0, fill="x")
        ctk.CTkLabel(frame_tel, text=f"📱 {pedido['telefone']}", font=("Arial", 14), text_color="#aaaaaa").pack(side="left")
        ctk.CTkButton(frame_tel, text="WhatsApp", width=70, height=24, font=("Arial", 11, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda t=pedido['telefone']: abrir_whatsapp(t)).pack(side="left", padx=15)
        
        ctk.CTkLabel(frame, text=f"📍 {pedido['endereco']}", font=("Arial", 15), wraplength=350, justify="left").pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(frame, text=f"📦 {pedido['conteudo']}", font=("Arial", 18, "bold"), text_color="#ffcc00", wraplength=350, justify="left").pack(anchor="w", padx=20, pady=10)
        ctk.CTkButton(frame, text="Fechar", command=janela.destroy, fg_color="#444444", hover_color="#333333", corner_radius=8).pack(pady=20)

    def abrir_edicao(self, pedido):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Editar Pedido #{pedido['id']}")
        janela.geometry("400x220")
        janela.configure(fg_color=BG_COLOR)
        janela.attributes("-topmost", True)
        janela.transient(self.winfo_toplevel())
        janela.grab_set()

        ctk.CTkLabel(janela, text="Editar Conteúdo da Entrega:", font=("Arial", 16, "bold"), text_color=BRAND_GREEN).pack(pady=(20, 10))
        entry_edit = criar_input(janela, "Conteúdo", 340)
        entry_edit.pack(pady=10)
        entry_edit.insert(0, pedido.get('conteudo') or "")

        def salvar():
            if entry_edit.get():
                self.controller.editar_conteudo_entrega(pedido['id'], entry_edit.get())
                janela.destroy()
        ctk.CTkButton(janela, text="Salvar Alteração", font=("Arial", 14, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, command=salvar).pack(pady=15)

    def desenhar_fila(self, entregas):
        self._draw_id += 1
        current_id = self._draw_id
        for widget in self.scroll_fila.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._draw_id or index >= len(entregas): return
            e = entregas[index]
            card = ctk.CTkFrame(self.scroll_fila, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=6, padx=10)
            ctk.CTkFrame(card, width=6, fg_color=BRAND_GREEN, corner_radius=10).pack(side="left", fill="y")
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            ctk.CTkLabel(info, text=f"#{e['id']} - {e['nome_cliente']}  |  📱 {e['telefone']}", font=("Arial", 16, "bold"), text_color="white", anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"📦 {e['conteudo']}", font=("Arial", 15), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(5,0))
            
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            ctk.CTkButton(botoes, text="WhatsApp", width=90, height=35, font=("Arial", 12, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda tel=e['telefone']: abrir_whatsapp(tel)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Ver Dados", width=90, height=35, font=("Arial", 12, "bold"), fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=e: self.abrir_detalhes(ped)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Editar", width=80, height=35, font=("Arial", 12, "bold"), fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=e: self.abrir_edicao(ped)).pack(side="left", padx=4)
            ctk.CTkButton(botoes, text="Entregue", width=100, height=35, font=("Arial", 12, "bold"), fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, corner_radius=6, command=lambda id=e['id']: self.controller.alterar_status(id, "entregue")).pack(side="left", padx=(15, 4))
            ctk.CTkButton(botoes, text="X", width=40, height=35, font=("Arial", 14, "bold"), fg_color="transparent", border_width=1, border_color=BRAND_RED, text_color=BRAND_RED, hover_color="#3a1114", corner_radius=6, command=lambda id=e['id']: self.controller.alterar_status(id, "cancelar")).pack(side="left", padx=4)
            
            self.after(15, lambda: animar(index + 1)) 
            
        animar(0)