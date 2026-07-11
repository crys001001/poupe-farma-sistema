import customtkinter as ctk
from view.config import BRAND_GREEN, BRAND_RED, BG_COLOR, CARD_COLOR, INPUT_BG, abrir_whatsapp

class AbaHistorico(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self.montar_ui()

    def montar_ui(self):
        top_hist = ctk.CTkFrame(self, fg_color="transparent")
        top_hist.pack(fill="x", padx=40, pady=(20,10))
        
        self.combo_tipo = ctk.CTkComboBox(top_hist, values=["Histórico de Entregas", "Log de Cadastros"], command=self.controller.mudar_filtro_historico, state="readonly", fg_color=INPUT_BG, border_width=0, width=200)
        self.combo_tipo.set("Histórico de Entregas")
        self.combo_tipo.pack(side="left")
        
        self.combo_filtro = ctk.CTkComboBox(top_hist, values=["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Tudo"], command=self.controller.mudar_filtro_historico, state="readonly", fg_color=INPUT_BG, border_width=0)
        self.combo_filtro.set("Hoje") 
        self.combo_filtro.pack(side="left", padx=10)
        
        botoes = ctk.CTkFrame(top_hist, fg_color="transparent")
        botoes.pack(side="right")
        ctk.CTkButton(botoes, text="📄 Gerar PDF", width=120, height=35, font=("Arial", 12, "bold"), fg_color="#D32F2F", hover_color="#9A0007", corner_radius=8, command=self.controller.exportar_pdf).pack(side="left", padx=5)
        ctk.CTkButton(botoes, text="📥 Fechamento Excel", width=140, height=35, font=("Arial", 12, "bold"), fg_color="#1E6E43", hover_color="#154d2f", corner_radius=8, command=self.controller.exportar_excel).pack(side="left")
        
        self.scroll_hist = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_hist.pack(pady=5, expand=True, fill="both")

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

    def desenhar_entregas(self, historico):
        self._draw_id += 1
        current_id = self._draw_id
        for widget in self.scroll_hist.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._draw_id or index >= len(historico): return
            h = historico[index]
            card = ctk.CTkFrame(self.scroll_hist, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=5, padx=10)
            
            cor = BRAND_GREEN if h['status'] == "Entregue" else BRAND_RED
            ctk.CTkFrame(card, width=6, fg_color=cor, corner_radius=10).pack(side="left", fill="y")
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            ctk.CTkLabel(info, text=f"Pedido #{h['id']} - {h['nome_cliente']}  |  📅 {h.get('data_formatada', 'N/A')}", font=("Arial", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"Status: {h['status'].upper()}  |  Conteúdo: {h['conteudo']}", font=("Arial", 14), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(3,0))
            
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            ctk.CTkButton(botoes, text="Detalhes", width=80, height=35, fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda ped=h: self.abrir_detalhes(ped)).pack(side="left")
            
            self.after(15, lambda: animar(index + 1))
            
        animar(0)
        
    def desenhar_log(self, cadastros):
        self._draw_id += 1
        current_id = self._draw_id
        for widget in self.scroll_hist.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._draw_id or index >= len(cadastros): return
            c = cadastros[index]
            card = ctk.CTkFrame(self.scroll_hist, fg_color=CARD_COLOR, corner_radius=10)
            card.pack(fill="x", pady=5, padx=10)
            ctk.CTkFrame(card, width=6, fg_color="#007ACC", corner_radius=10).pack(side="left", fill="y")
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            ctk.CTkLabel(info, text=f"👤 {c['nome']}  |  📅 Registrado em: {c.get('data_formatada', 'N/A')}", font=("Arial", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info, text=f"Telefone: {c['telefone']} | Endereço: {c['endereco']}", font=("Arial", 14), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(3,0))
            
            self.after(15, lambda: animar(index + 1))
            
        animar(0)