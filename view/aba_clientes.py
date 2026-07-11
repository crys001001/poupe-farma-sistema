import customtkinter as ctk
from view.config import BRAND_GREEN, BRAND_GREEN_HOVER, BRAND_RED, BRAND_RED_HOVER, BG_COLOR, CARD_COLOR, INPUT_BG, criar_input, abrir_whatsapp

class AbaClientes(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._draw_id = 0
        self.montar_ui()

    def montar_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(pady=(20, 10), fill="x", padx=40)
        
        self.entry_pesquisa = criar_input(top_bar, "🔍 Buscar cliente...", 550)
        self.entry_pesquisa.pack(side="left", padx=(0, 10))
        self.entry_pesquisa.bind("<KeyRelease>", self.controller.filtrar_clientes)
        
        ctk.CTkButton(top_bar, text="Atualizar", command=self.controller.carregar_clientes, width=120, height=50, font=("Arial", 14, "bold"), fg_color="#444444", hover_color="#333333", corner_radius=8).pack(side="right")
        
        self.scroll_lista = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_lista.pack(pady=10, expand=True, fill="both")

    def get_pesquisa(self): 
        return self.entry_pesquisa.get().lower()

    def abrir_dados(self, cliente):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Dados: {cliente.get('nome','')}")
        janela.geometry("400x480")
        janela.attributes("-topmost", True)
        janela.configure(fg_color=BG_COLOR)

        ctk.CTkLabel(janela, text="Ficha Completa", font=("Arial", 20, "bold"), text_color=BRAND_GREEN).pack(pady=15)
        
        textbox = ctk.CTkTextbox(janela, font=("Arial", 16), width=360, height=350, fg_color=INPUT_BG)
        textbox.pack(padx=20, pady=10, fill="both", expand=True)

        texto = f"NOME:\n{cliente.get('nome','')}\n\nTELEFONE:\n{cliente.get('telefone','')}\n\nENDEREÇO:\n{cliente.get('endereco','')}\n\nNÚMERO:\n{cliente.get('numero','')}\n\nBAIRRO:\n{cliente.get('bairro') or ''}\n\nCOMPLEMENTO:\n{cliente.get('complemento') or ''}\n\nFALTOU NA LOJA:\n{cliente.get('produto_desejo') or ''}"
        textbox.insert("0.0", texto)
        textbox.configure(state="disabled")

    def abrir_edicao(self, cliente):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Editar: {cliente.get('nome','')}")
        janela.geometry("500x680")
        janela.configure(fg_color=BG_COLOR)
        janela.attributes("-topmost", True)
        
        container = ctk.CTkFrame(janela, fg_color="transparent")
        container.pack(expand=True)
        
        ctk.CTkLabel(container, text="Editar Dados do Cliente", font=("Arial", 20, "bold"), text_color=BRAND_GREEN).pack(pady=(0, 20))
        
        ctk.CTkLabel(container, text="Nome Completo", font=("Arial", 12)).pack(anchor="w")
        e_nome = criar_input(container, "Nome", 450)
        e_nome.insert(0, cliente.get('nome') or "")
        e_nome.pack(pady=(0, 10))
        
        ctk.CTkLabel(container, text="Endereço", font=("Arial", 12)).pack(anchor="w")
        e_end = criar_input(container, "Endereço", 450)
        e_end.insert(0, cliente.get('endereco') or "")
        e_end.pack(pady=(0, 10))
        
        fd = ctk.CTkFrame(container, fg_color="transparent")
        fd.pack(pady=(0, 10), fill="x")
        
        f_num = ctk.CTkFrame(fd, fg_color="transparent")
        f_num.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(f_num, text="Nº", font=("Arial", 12)).pack(anchor="w")
        e_num = criar_input(f_num, "Nº", 100)
        e_num.insert(0, cliente.get('numero') or "")
        e_num.pack()
        
        f_bairro = ctk.CTkFrame(fd, fg_color="transparent")
        f_bairro.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(f_bairro, text="Bairro", font=("Arial", 12)).pack(anchor="w")
        e_bairro = criar_input(f_bairro, "Bairro", 150)
        e_bairro.insert(0, cliente.get('bairro') or "")
        e_bairro.pack()

        f_comp = ctk.CTkFrame(fd, fg_color="transparent")
        f_comp.pack(side="left")
        ctk.CTkLabel(f_comp, text="Complemento", font=("Arial", 12)).pack(anchor="w")
        e_comp = criar_input(f_comp, "Comp", 190)
        e_comp.insert(0, cliente.get('complemento') or "")
        e_comp.pack()
        
        ctk.CTkLabel(container, text="Desejo / Faltou na Loja", font=("Arial", 12), text_color="#E5B800").pack(anchor="w", pady=(5,0))
        e_desejo = criar_input(container, "Desejo / Falta", 450)
        e_desejo.insert(0, cliente.get('produto_desejo') or "")
        e_desejo.pack(pady=(0, 20))
        
        def salvar():
            dados = {
                "telefone": cliente.get('telefone', ''), 
                "nome": e_nome.get(), 
                "endereco": e_end.get(), 
                "numero": e_num.get(), 
                "bairro": e_bairro.get(),
                "complemento": e_comp.get(), 
                "produto_desejo": e_desejo.get()
            }
            self.controller.api.salvar_cliente(dados)
            self.controller.carregar_clientes()
            janela.destroy()
            
        ctk.CTkButton(container, text="Salvar Alterações", width=450, height=50, fg_color=BRAND_GREEN, hover_color=BRAND_GREEN_HOVER, font=("Arial", 16, "bold"), command=salvar).pack(pady=10)

    def desenhar_lista(self, lista):
        self._draw_id += 1
        current_id = self._draw_id
        for widget in self.scroll_lista.winfo_children(): widget.destroy()

        def animar(index):
            if current_id != self._draw_id or index >= len(lista): return
            c = lista[index]
            card = ctk.CTkFrame(self.scroll_lista, fg_color=CARD_COLOR, corner_radius=12)
            card.pack(fill="x", pady=6, padx=10)
            
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=20, pady=15)
            ctk.CTkLabel(info, text=c['nome'], font=("Arial", 18, "bold")).pack(anchor="w")
            
            bairro_text = f" - {c.get('bairro')}" if c.get('bairro') else ""
            ctk.CTkLabel(info, text=f"📱 {c['telefone']}   |   📍 {c['endereco']}, {c['numero']}{bairro_text}", font=("Arial", 14), text_color="#aaaaaa").pack(anchor="w", pady=(5,0))
            
            if c.get('produto_desejo'):
                ctk.CTkLabel(info, text=f"⚠️ Faltou na loja: {c['produto_desejo']}", font=("Arial", 13, "italic"), text_color="#E5B800").pack(anchor="w", pady=(2,0))
            
            botoes = ctk.CTkFrame(card, fg_color="transparent")
            botoes.pack(side="right", padx=15)
            
            ctk.CTkButton(botoes, text="Ver Dados", width=80, height=30, fg_color="#333333", hover_color="#444444", corner_radius=6, command=lambda cli=c: self.abrir_dados(cli)).pack(pady=2)
            ctk.CTkButton(botoes, text="WhatsApp", width=80, height=30, font=("Arial", 11, "bold"), fg_color="#25D366", hover_color="#128C7E", corner_radius=6, command=lambda tel=c['telefone']: abrir_whatsapp(tel)).pack(pady=2)
            ctk.CTkButton(botoes, text="Editar", width=80, height=30, fg_color="#3a3a3a", hover_color="#555555", corner_radius=6, command=lambda cli=c: self.abrir_edicao(cli)).pack(pady=2)
            ctk.CTkButton(botoes, text="Excluir", width=80, height=30, fg_color=BRAND_RED, hover_color=BRAND_RED_HOVER, text_color="white", corner_radius=6, command=lambda tel=c['telefone']: self.controller.excluir_cliente(tel)).pack(pady=2)
            
            self.after(15, lambda: animar(index + 1)) 

        animar(0)